import os
from dotenv import load_dotenv
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# Load environment variables from .env file
load_dotenv()

# Use environment variable for the token
hf_token = os.getenv("HUGGINGFACE_TOKEN")

def generate_recipe(model, tokenizer, prompt):
    inputs = tokenizer(prompt, return_tensors="pt")
    with torch.no_grad():
        output = model.generate(
            inputs.input_ids,
            max_length=350,
            num_return_sequences=1,
            do_sample=True,
            temperature=0.7,
            top_k=50,
            top_p=0.75,
            repetition_penalty=1.2
        )
    
    # Decode the output, excluding the input prompt
    full_output = tokenizer.decode(output[0], skip_special_tokens=True)
    return full_output[len(prompt):].strip()

# Load the original model
original_model_name = "facebook/opt-125m"
original_tokenizer = AutoTokenizer.from_pretrained(original_model_name, use_auth_token=hf_token)
original_model = AutoModelForCausalLM.from_pretrained(original_model_name, use_auth_token=hf_token)

# Load the fine-tuned model
finetuned_model_path = "/app/finetuned_model"
# "/app/finetuned_model"
finetuned_tokenizer = AutoTokenizer.from_pretrained(finetuned_model_path, use_auth_token=hf_token)
finetuned_model = AutoModelForCausalLM.from_pretrained(finetuned_model_path, use_auth_token=hf_token)

# Prepare your prompt
prompt = """Please write a low-sodium meal recipe that takes approximately 55 minutes 
            and includes the following ingredients: tomato, beef. 
            The recipe should be formatted with a clear list of ingredients and detailed, step-by-step cooking instructions."""

# Generate recipes using both models
original_recipe = generate_recipe(original_model, original_tokenizer, prompt)
finetuned_recipe = generate_recipe(finetuned_model, finetuned_tokenizer, prompt)

# Print the results
print("Original Model Output:")
print(original_recipe)
print("\n" + "="*50 + "\n")
print("Fine-tuned Model Output:")
print(finetuned_recipe)
