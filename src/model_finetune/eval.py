from unsloth import FastLanguageModel
from nmt_bleu import compute_bleu


def evaluate_model(model, tokenizer, eval_dataset, device, max_new_tokens=2500):
    print("Evaluating start...")
    FastLanguageModel.for_inference(model)
    model.to(device)
    print("Model for inference loaded.")

    predictions, references = [], []

    # Process each example in the dataset
    print("Generate outputs for BLEU...")
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

    result = compute_bleu(predictions=predictions, references=references)
    return result["bleu"]
