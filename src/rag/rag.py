import json
import os
import sys

import torch
from dotenv import load_dotenv
from google.cloud import storage
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFacePipeline
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

# Add parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set environment variables
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/app/secrets/recipe.json'
# '/Users/graceguo/Desktop/harvard/AC215/Project/Fine-tuning/secrets/recipe.json'

# Load environment variables
load_dotenv()

# Get the Hugging Face token from the environment
hf_token = os.getenv("HUGGINGFACE_TOKEN")

# Load the llm
print("Loading the model...")
model_path = "facebook/opt-125m"
tokenizer = AutoTokenizer.from_pretrained(model_path, use_auth_token=hf_token)
model = AutoModelForCausalLM.from_pretrained(model_path, use_auth_token=hf_token)
print("Model loaded successfully.")

# Update the device selection
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Move the model to the selected device
model = model.to(device)

print("HuggingFacePipeline created.")

pipe_before = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    max_length=256,  
    temperature=0.4,  # Increased to make the generation more creative
    top_p=0.95,       # Decreased to make the output more focused
    repetition_penalty=0.8,  # Increased to further avoid repetition
    device=device,
    truncation=True,
    return_full_text=False,
    do_sample=True
)

llm_before = HuggingFacePipeline(pipeline=pipe_before)

# Update the pipeline creation
pipe = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    max_length=1024,  
    temperature=0.7,
    top_p=0.95, 
    repetition_penalty=1.2,
    device=device,
    truncation=True,
    return_full_text=False,
    do_sample=True
)

llm = HuggingFacePipeline(pipeline=pipe)

# Create a knowledge base from the recipes
def load_recipes():
    print("Loading recipes from GCS...")
    storage_client = storage.Client()
    bucket = storage_client.bucket("recipe-dataset")
    blob = bucket.blob("processed/fine_tuning_data_top_1000.jsonl")
    
    content = blob.download_as_text()
    recipes = []
    for line in content.split('\n'):
        if line.strip():
            recipe = json.loads(line)
            recipes.append(recipe["completion"])
    print(f"Loaded {len(recipes)} recipes.")
    
    # Create a text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    
    # Split the recipes into chunks
    chunks = text_splitter.create_documents(recipes)
    print(f"Created {len(chunks)} chunks from the recipes.")
    return chunks

recipes = load_recipes()

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

def rag_chain(embedding_model, llm, recipe_chunks, query):
    print("Starting RAG chain...")
    # Create a vector store from the recipe chunks
    print("Creating vector store...")
    try:
        vectorstore = FAISS.from_documents(recipe_chunks, embedding_model)
        print("Vector store created successfully.")
    except Exception as e:
        print(f"Error creating vector store: {str(e)}")
        return None

    # Create a retriever object from the vector store for efficient document retrieval
    print("Creating retriever...")
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3}) 

    # Print the retrieved context
    print("Retrieving relevant documents...")
    retrieved_docs = retriever.get_relevant_documents(query)
    print("\nRetrieved Context:")
    for i, doc in enumerate(retrieved_docs, 1):
        print(f"\nDocument {i}:")
        print(doc.page_content)

    # Define a template string for prompting the LLM with context and query
    print("Creating prompt template...")
    template = """
    You are an assistant for generating recipes. Use the following pieces of retrieved context to create a recipe based on the user's request.
    The Generated Recipe should only include a title, a list of ingredients, and step-by-step cooking instructions.
    Your response should only include the generated recipe in text.
    User Request: {request}
    Retrieved Recipes: {context}
    
    Generated Recipe:
    """

    # Create a ChatPromptTemplate object from the template string
    prompt = ChatPromptTemplate.from_template(template)

    # Define the RAG chain using LangChain components
    print("Defining RAG chain...")
    chain = (
        {"context": retriever, "request": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    print("Invoking RAG chain...")
    result = chain.invoke(query)
    print("RAG chain completed.")
    
    return result

def compare_results(query):
    print('***Comparing results***')
    print("\nGenerating recipe with original settings...")
    recipe_original = rag_chain(embeddings, llm_before, recipes, query)
    if recipe_original:
        print("\nGenerated Recipe with Original Settings:")
        print(recipe_original)
    else:
        print("Failed to generate a valid recipe with original settings.")

    print("\nGenerating recipe with updated settings...")
    recipe_updated = rag_chain(embeddings, llm, recipes, query)
    if recipe_updated:
        print("\nGenerated Recipe with Updated Settings:")
        print(recipe_updated)
    else:
        print("Failed to generate a valid recipe with updated settings.")

# Main function
if __name__ == "__main__":
    query = """Please write a low-sodium meal recipe that takes approximately 55 minutes 
               and includes the following ingredients: tomato, beef. 
               The recipe should be formatted with a clear list of ingredients and cooking instructions."""
    
    print("\nGenerating recipe...")
    recipe = rag_chain(embeddings, llm, recipes, query)
    if recipe:
        print("\nGenerated Recipe:")
        print(recipe)
    else:
        print("Failed to generate a valid recipe.")
    
    # compare_results(query)

