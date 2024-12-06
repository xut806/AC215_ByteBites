import evaluate
from unsloth import FastLanguageModel


def evaluate_model(model, tokenizer, eval_dataset, device, max_new_tokens=2500):
    FastLanguageModel.for_inference(model)
    model.to(device)

    bleu_metric = evaluate.load("bleu")
    predictions, references = [], []

    # Process each example in the dataset
    for example in eval_dataset:
        prompt = example["prompt"]

        inputs = tokenizer(
            prompt,
            return_tensors="pt",
            max_length=tokenizer.model_max_length,
            truncation=True,
        ).to(device)
        outputs = model.generate(
            **inputs, max_new_tokens=max_new_tokens, use_cache=True
        )

        decoded_preds = tokenizer.batch_decode(outputs, skip_special_tokens=True)
        decoded_labels = [example["completion"]]

        predictions.extend(decoded_preds)
        references.extend([[ref] for ref in decoded_labels])

    result = bleu_metric.compute(predictions=predictions, references=references)
    return result["bleu"]
