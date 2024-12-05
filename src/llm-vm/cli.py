import os
import zipfile
from google.cloud import storage
import logging
from transformers import TextStreamer
from unsloth import FastLanguageModel
from fastapi import FastAPI, HTTPException
import uvicorn
import re

app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RecipeGenerator:
    def __init__(
        self,
        bucket_name,
        blob_name,
        local_file_path,
        destination_folder,
        model_id=None,
        max_seq_length=2048,
        load_in_4bit=True,
    ):
        self.bucket_name = bucket_name
        self.blob_name = blob_name
        self.local_file_path = local_file_path
        self.destination_folder = destination_folder
        self.model_id = model_id
        self.max_seq_length = max_seq_length
        self.load_in_4bit = load_in_4bit
        self.model = None
        self.tokenizer = None
        self.text_streamer = None

    def get_latest_checkpoint(self):
        try:
            checkpoints = [
                d
                for d in os.listdir(self.destination_folder)
                if os.path.isdir(os.path.join(self.destination_folder, d))
            ]
            sorted_checkpoints = sorted(
                checkpoints, key=lambda x: int(re.search(r"\d+", x).group())
            )
            if not sorted_checkpoints:
                raise Exception(
                    "No checkpoints found in the extracted model directory."
                )

            base_folder = (
                self.destination_folder[2:]
                if self.destination_folder.startswith("./")
                else self.destination_folder
            )
            return f"{base_folder}/{sorted_checkpoints[-1]}"

        except Exception as e:
            logger.error(f"Error finding the latest checkpoint: {e}")
            raise HTTPException(
                status_code=500, detail=f"Error finding latest checkpoint: {e}"
            )

    def download_and_extract_model(self):
        try:
            client = storage.Client()
            bucket = client.bucket(self.bucket_name)
            blob = bucket.blob(self.blob_name)
            blob.download_to_filename(self.local_file_path)

            logger.info(
                f"Downloaded {self.blob_name} from {self.bucket_name} to {self.local_file_path}"
            )

            os.makedirs(self.destination_folder, exist_ok=True)

            with zipfile.ZipFile(self.local_file_path, "r") as zip_ref:
                zip_ref.extractall(self.destination_folder)

            logger.info(f"Extracted model files to {self.destination_folder}")

            self.model_id = self.get_latest_checkpoint()
            logger.info(f"Newest checkpoint identified: {self.model_id}")

        except Exception as e:
            logger.error(f"Failed to download or extract the model: {e}")
            raise HTTPException(
                status_code=500, detail=f"Model download or extraction failed: {e}"
            )

    def load_and_prepare_model(self):
        try:
            logger.info(f"Loading model from: {self.model_id}")
            self.model, self.tokenizer = FastLanguageModel.from_pretrained(
                model_name=self.model_id,
                max_seq_length=self.max_seq_length,
                load_in_4bit=self.load_in_4bit,
            )
            logger.info("Finetuned model and tokenizer loaded successfully.")

            FastLanguageModel.for_inference(self.model)
            self.text_streamer = TextStreamer(self.tokenizer)

        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise HTTPException(status_code=500, detail=f"Model loading failed: {e}")

    def generate_recipe(self, prompt, max_new_tokens=1024, stream_output=False):
        try:
            inputs = self.tokenizer(prompt, return_tensors="pt")

            if stream_output and self.text_streamer:
                _ = self.model.generate(
                    **inputs, streamer=self.text_streamer, max_new_tokens=max_new_tokens
                )
                return None
            else:
                outputs = self.model.generate(**inputs, max_new_tokens=max_new_tokens)
                return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        except Exception as e:
            logger.error(f"Error during text generation: {e}")
            raise HTTPException(status_code=500, detail=f"Text generation failed: {e}")


# Initialize recipe generator
bucket_name = "ai-recipe-trainer"
blob_name = "finetuned_models/finetuned_model.zip"
local_file_path = "finetuned_model.zip"
destination_folder = "./finetuned_model"
# model_id = "finetuned_model/checkpoint-500"
max_seq_length = 2048
load_in_4bit = True

recipe_generator = RecipeGenerator(
    bucket_name=bucket_name,
    blob_name=blob_name,
    local_file_path=local_file_path,
    destination_folder=destination_folder,
    model_id=None,
    max_seq_length=max_seq_length,
    load_in_4bit=load_in_4bit,
)


@app.on_event("startup")
async def startup_event():
    try:
        logger.info("Downloading and extracting the model...")
        recipe_generator.download_and_extract_model()

        logger.info("Loading the model...")
        recipe_generator.load_and_prepare_model()

        logger.info("Recipe generator is ready for use.")
    except Exception as e:
        logger.error(f"Failed during startup: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to initialize the recipe generator."
        )


# Endpoints
@app.post("/generate/")
async def generate_text(request: dict):
    try:
        input_text = request.get("text", "")
        max_length = request.get("max_length", 150)

        if not input_text:
            raise HTTPException(status_code=400, detail="Input text is required.")

        logger.info(
            f"Received generation request with prompt: {input_text} and max_length={max_length}"
        )

        generated_text = recipe_generator.generate_recipe(
            prompt=input_text, max_new_tokens=max_length, stream_output=False
        )
        return {"generated_text": generated_text}

    except Exception as e:
        logger.error(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating text: {e}")


@app.get("/health")
async def health():
    if recipe_generator.model is None:
        raise HTTPException(status_code=503, detail="Model not loaded.")
    return {"status": "healthy", "model": recipe_generator.model_id}


# Run FastAPI app
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
