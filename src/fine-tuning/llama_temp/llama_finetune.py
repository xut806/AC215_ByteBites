from trl import SFTConfig, SFTTrainer
import torch
from datasets import Dataset
import pandas as pd
from transformers import AutoTokenizer, AutoModelForCausalLM, Trainer, TrainingArguments, DataCollatorForLanguageModeling
from unsloth import is_bfloat16_supported
import wandb
from huggingface_hub import login
from unsloth import FastLanguageModel

from google.cloud import storage
from io import BytesIO

print("running llama_finetune.py")

bucket_name = 'ai-recipe-data'
train_blob_name = 'processed/fine_tuning_llama_train_data.jsonl'
MODEL_NAME = 'unsloth/Llama-3.2-3B-bnb-4bit'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/app/secrets/data-service-account.json'
os.environ['WANDB_API'] = '/app/secrets/wandb_api_key'
os.environ['HUGGINGFACE_HUB_TOKEN'] = '/app/secrets/huggingface_token'

client = storage.Client.from_service_account_json(GOOGLE_APPLICATION_CREDENTIALS)
bucket = client.get_bucket(bucket_name)
blob = bucket.blob(train_blob_name)
train_data_bytes = blob.download_as_bytes()
train_data = pd.read_json(BytesIO(train_data_bytes), lines=True)
train_data = Dataset.from_pandas(train_data)

print("**train_data: **", train_data)

login(token=os.environ['HUGGINGFACE_HUB_TOKEN'])

MAX_SEQ_LENGTH = 5020
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name=MODEL_NAME,
    max_seq_length=MAX_SEQ_LENGTH,
    load_in_4bit=True,
    dtype=None,
)

model = FastLanguageModel.get_peft_model(
    model,
    r=16,
    lora_alpha=16,
    lora_dropout=0,
    target_modules=["q_proj", "k_proj", "v_proj", "up_proj", "down_proj", "o_proj", "gate_proj"],
    use_rslora=True,
    use_gradient_checkpointing="unsloth",
    random_state=32,
    loftq_config=None,
)

model.gradient_checkpointing_enable()

wandb.login(key=os.environ['WANDB_API'])

wandb.init(project="llama_3b_finetune_gpu")

training_args = SFTConfig(
    learning_rate=3e-4,
    lr_scheduler_type="linear",
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    num_train_epochs=1,
    fp16=not torch.cuda.is_bf16_supported(),
    bf16=torch.cuda.is_bf16_supported(),
    logging_steps=50,
    max_steps=3,
    optim="adamw_8bit",
    weight_decay=0.01,
    warmup_steps=int(0.1 * (len(train_data) / 2)), # 10% of training steps for warmup
    output_dir="/app/finetuned_model",
    logging_dir="/app/logs",
    seed=0,
    remove_unused_columns=True,
)

trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=train_data,
    dataset_text_field="text",
    max_seq_length=MAX_SEQ_LENGTH,
    dataset_num_proc=2,
    packing=True,
    args=training_args,
)
print("Trainning start...")
trainer.train()
print("Trainning finished...")

wandb.finish()

