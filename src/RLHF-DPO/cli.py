from unsloth import FastLanguageModel
from unsloth import PatchDPOTrainer, is_bfloat16_supported
from datasets import DatasetDict, Dataset
from trl import DPOTrainer, DPOConfig
import json

PatchDPOTrainer()


max_seq_length = 4096
dtype = None
load_in_4bit = True

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="finetuned_model/checkpoint-4428",
    max_seq_length=max_seq_length,
    dtype=dtype,
    load_in_4bit=load_in_4bit,
)

file_path = "./spicy_recipes.json"

# Load the data
with open(file_path, "r") as file:
    data = json.load(file)

dataset = DatasetDict(
    {
        "train": Dataset.from_list(data["train"]),
        "test": Dataset.from_list(data["test"]),
    }
)


def apply_chat_template(example, tokenizer, task):
    prompt = example["prompt"]
    chosen = example["chosen"]
    rejected = example["rejected"]

    prompt_tokenized = tokenizer(prompt, truncation=True, padding="max_length")
    chosen_tokenized = tokenizer(chosen, truncation=True, padding="max_length")
    rejected_tokenized = tokenizer(rejected, truncation=True, padding="max_length")

    return {
        "prompt": prompt,
        "prompt_tokenized": prompt_tokenized,
        "chosen": chosen,
        "chosen_tokenized": chosen_tokenized,
        "rejected": rejected,
        "rejected_tokenized": rejected_tokenized,
    }


raw_datasets = dataset.map(
    apply_chat_template,
    fn_kwargs={"tokenizer": tokenizer, "task": "dpo"},
    num_proc=2,
    remove_columns=dataset["train"].column_names,
    desc="Formatting comparisons with prompt template",
)

dpo_trainer = DPOTrainer(
    model=model,
    ref_model=None,
    args=DPOConfig(
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        warmup_ratio=0.1,
        num_train_epochs=3,
        learning_rate=5e-6,
        fp16=not is_bfloat16_supported(),
        bf16=is_bfloat16_supported(),
        logging_steps=1,
        optim="adamw_8bit",
        weight_decay=0.0,
        lr_scheduler_type="linear",
        seed=42,
        output_dir="outputs",
        report_to="none",
    ),
    beta=0.1,
    train_dataset=raw_datasets["train"],
    eval_dataset=raw_datasets["test"],
    tokenizer=tokenizer,
    max_length=1024,
    max_prompt_length=512,
)

dpo_trainer.train()
