# ByteBites: Recipe Generation
<img src="./reports/logo2.png" alt="bytebites-logo" width="500"/>


## Project Info
In our project, we aim to develop a web application that integrates LLMs with Nutritional Science and provides a user-friendly interface to personalize recipe suggestions based on available ingredients while providing nutritional insights for the user. 

### Team Members
| Name         | GitHub Profile                   |
|--------------|----------------------------------|
| Grace Guo     | [@gguo78](https://github.com/gguo78) |
| Yilin Qi       | [@yilinnq](https://github.com/yilinnq) |
| Xu Tang   | [@xut806](https://github.com/xut806) |


## Directory Structure

Our repo is structured as follows:

```
├── reports/                 # Application mock-up and interactive prototype
│    ├── logo.png            # [New in MS4] new ByteBites logo
│    ├── logo2.png           # [New in MS4] new ByteBites logo 
│    ├── AC215_webapp_prototype.pdf      
│    ├── Midterm_Presentation.pdf   # Presentation slides PDF version
│    ├── Midterm_Presentation.pptx   # Presentation slides PPTX version  
│    └── prototype_link.md
│    
├── notebooks/               # [New in MS4] In-progress notebooks demonstrating experiments
│    ├── rlaif_peft_finetuned_opt125m.ipynb    # We attempt to implement RLAIF (where the LLM labeler is the off-the-shelf llama-3.1-8b model) on top of our finetuned opt125m model with LoRA
│    
├── src/                     # Source code directory
│    ├── ocr/                # Implementing OCR and NER for ingredient recognition from receipt
│         ├── ocr_ner.py   
│         ├── extract_ingredients.py 
│         ├── docker-shell.sh   
│         ├── docker-entrypoint.sh  
│         ├── Dockerfile   
│         ├── Pipfile   
│         └── Pipfile.lock
│         
│    ├── preprocessing/       #  Preprocessing raw recipe data from a Google Cloud Storage bucket and prepare it for fine-tuning.        
│         ├── data_preprocessing.py    
│         ├── docker-shell.sh   
│         ├── docker-entrypoint.sh  
│         ├── Dockerfile   
│         ├── Pipfile   
│         └── Pipfile.lock
│
│    ├── fine-tuning/             # Fine-tuning LLM using the preprocessed recipe data.
|         ├── inference+nutrition.py  # [New in MS4] Please run this script to get the generated recipe and the nutrition facts   
│         ├── utils.py   
│         ├── fine_tune.py    
│         ├── compare_models.py   
│         ├── docker-shell.sh   
│         ├── docker-entrypoint.sh  
│         ├── Dockerfile   
│         ├── Pipfile   
│         └── Pipfile.lock
│
│    ├── rag/                     # Implementing RAG workflow for generating recipes based on user queries
│         ├── rag.py   
│         ├── docker-shell.sh   
│         ├── docker-entrypoint.sh  
│         ├── Dockerfile   
│         ├── Pipfile   
│         └── Pipfile.lock
│     
│    ├── landing/               # Frontend for the application
│         ├── .env.local        # Secret keys
│         ├── Dockerfile        # Dockerfile for the frontend
│    ├── api-service/          # Backend for the application
│         ├── api/
|         ├── Dockerfile        
│         ├── Pipfile            
│         ├── Pipfile.lock
|         ├── docker-entrypoint.sh
│         ├── docker-shell.sh
│    └── .env
├── .gitignore
├── README.md
├── LICENSE
├── secrets/                      # Secrets directory
│    └── recipe.json
```

Please make sure to create an `.env` file that contains your Huggingface Access Token (`HUGGINGFACE_TOKEN`) and your USDA API key (`USDA_API_KEY`) as well as a `secrets/` directory with your credentials in the location as shown above after cloning the repo.

## Updates 📢
- [NEW IN MS4] Designed new logos for BiteBytes! (Please check out our `reports/` folder)
- [NEW IN MS4] Added finetuned model inference and nutrition facts (Please see [Container 3: Fine-Tuning](#container-3-fine-tuning))
- [NEW IN MS4] Experimenting with RLAIF (Please check out our `notebooks/` folder)
- [NEW IN MS4] Added frontend (Please see [Frontend & Backend](#frontend--backend))
- [NEW IN MS4] Added OCR and NER API (Please see [Frontend & Backend](#frontend--backend))
- [NEW IN MS4] Added CI and testing (Please see [CI & Testing](#ci--testing))
- [NEW IN MS4] Llama-3.2-3b (recipe generator model) finetuned on GCP
- [NEW IN MS4] Llama-3.2-3b deployed and served on GCP (external IP: 34.41.18.132)

## Aplication Design

Before we start implementing the app we built a detailed design document outlining the application’s architecture. We built a Solution Architecture and Technical Architecture to ensure all our components work together.

---
Here is our Solution Architecture:
 ![image](./screenshots/sol_arch.png)
 
 ![image](./screenshots/sol_arch2.png)

Here is our Technical Architecture
 ![image](./screenshots/tech_arch.png)

## Backend API

"We built backend api service using fast API to expose model functionality to the frontend. We also added apis that will help the frontend display some key information about the model and data."
 ![image](./screenshots/fastapi.png)

  ![image](./screenshots/fastapi_ocr.png)
  
   ![image](./screenshots/fastapi_llm.png)

## Table of Contents
1. [Virtual Environment Setup & Containers](#virtual-environment-setup--containers)
2. [Data Versioning Strategy](#data-versioning-strategy)
3. [LLM: Fine-tuning](#llm-fine-tuning)
4. [LLM: RAG](#llm-rag)
5. [APIs & Frontend Implementation](#apis--frontend-implementation)
6. [CI & Testing](#ci--testing)
7. [Deployment with Ansible]()


## Virtual Environment Setup & Containers

We have three containers for this project and each container serves a specific purpose within the project, including data preprocessing, fine-tuning, and RAG (Retrieval-Augmented Generation).

### Container 1: OCR & NER (NEW IN MS3)

- **Purpose**: To recognize text from receipt images (OCR) and then recognize edible ingredients (NER).

- **Files**:
  - `Dockerfile`: Defines the environment and dependencies for ocr and ner processing.
  - `Pipfile`: Manages Python packages.
  - `ocr_ner.py`/`extract_ingredients.py`: Two scripts serve the same function and contain the OCR & NER logic. The pre-trained OCR package, `docTR`, is used for text recognition from receipt images, whereas the pre-trained NER model specific to food entities, `InstaFoodRoBERTa-NER` is used for NER. We uploaded the [ExpressExpense](https://expressexpense.com/blog/free-receipt-images-ocr-machine-learning-dataset/) dataset, which is a set of 200 receipt images, to a GCS bucket; this script downloads the data from the GCS bucket and then conducts OCR and NER. It uploads the recognized ingredients as a .json file to the GCS bucket.
  - `docker-entrypoint.sh`: Entry point script for the container.

- **Instructions**:
  - In the `/ocr` directory, run `sh docker-shell.sh` to start the container.
  - Once the container is running, run `python ocr_ner.py` or `python extract_ingredients.py` to start the OCR & NER processing.

### Container 2: Data Preprocessing

- **Purpose**: To process raw recipe data from a Google Cloud Storage bucket and prepare it for fine-tuning and rag tasks. 

- **Files**:
  - `Dockerfile`: Defines the environment and dependencies for data preprocessing.
  - `Pipfile`: Manages Python packages.
  - `data_preprocessing.py`: Contains the preprocessing logic, where we fetch the data from the Google Cloud Storage bucket and upload the processed data to Google Cloud Storage for the next container.
  - `docker-entrypoint.sh`: Entry point script for the container.

- **Instructions**: 
  - In the `/preprocessing` directory, run `sh docker-shell.sh` to start the container.
  - Once the container is running, run `python data_preprocessing.py` to start the data preprocessing.

- **Screenshot**: 

  ![image](./screenshots/llm-data-preprocessor.png) 

### Container 3: Fine-Tuning

- **Purpose**: To fine-tune the language model using the preprocessed recipe data.

- **Files**:
  - `Dockerfile`: Sets up the environment for fine-tuning.
  - `Pipfile`: Manages Python packages.
  - `fine_tune.py`: Contains the fine-tuning logic.
  - `utils.py`: Contains the utility functions for fine-tuning.
  - `upload.py`: Upload the model.safetensors file of the finetuned model to GCP bucket.
  - `docker-entrypoint.sh`: Entry point script for the container.
  - **`inference+nutrition.py`**: Loads the finetuned model using the `model.safetensors` file from the `finetuned_model/` folder on our GCP bucket, generates a recipe with our finetuned model, and obtains the nutrition fact of the recipe by calling the USDA API. The generated recipe is uploaded to the `generated_recipe/` folder on our GCP bucket, and the nutrition facts is uploaded to the `nutrition_facts/` folder on our GCP bucket. An example of the nutrition facts uploaded to our GCP bucket:
      - ![image](./screenshots/nutrition_facts.png) 
  - `compare_models.py`: Contains the logic to load the finetuned model from the `model.safetensors` file from the GCP bucket, then compare the performance of the fine-tuned model with the base model.

- **Instructions**:
  - In the `/fine-tuning` directory, run `sh docker-shell.sh` to start the container.
  - Once the container is running, run `python fine_tune.py` to start the fine-tuning. You may choose not to run this step, because we have already fine-tuned and copied the model to the container. (However, due to the size of the model, we did not push it to Github.)
  - You can run `python compare_models.py` to compare the performance of the fine-tuned model with the base model.

- **Screenshot**: 

  ![image](./screenshots/llm-fine-tuner.png)   

### Container 4: RAG (Retrieval-Augmented Generation)

- **Purpose**: To implement the RAG workflow for generating recipes based on user queries.

- **Files**:
  - Dockerfile: Defines the environment for the RAG server.
  - Pipfile: Manages Python packages.
  - rag.py: Contains the RAG implementation.
  - docker-entrypoint.sh: Entry point script for the container.

- **Instructions**:
  - In the `/rag` directory, run `sh docker-shell.sh` to start the container.
  - Once the container is running, run `python rag.py` to start the RAG server and see the results.

- **Screenshot**: 

  ![image](./screenshots/llm-rag-server.png)  

## Data Versioning Strategy

The raw data we used for our project is the [Food.com Recipes and Interactions](https://www.kaggle.com/datasets/shuyangli94/food-com-recipes-and-user-interactions?select=RAW_recipes.csv) dataset on Kaggle. The raw dataset lives on a GCS bucket so that it can be downloaded and preprocessed for our finetuning and rag task. The preprocessed data is also stored on the GCS bucket (please check [Container 1: Data Preprocessing](#container-1-data-preprocessing) for details).

For this milestone, we have adopted the GCS bucket versioning feature for data versioning. In particular, we set the max. number of versions per object to 1 and set the expiration timeframe for noncurrent versions to 7 days. 

## LLM: Fine-tuning

- **Overview**: In this Milestone, we perform fine-tuning on the [`facebook/opt-125m`](https://huggingface.co/facebook/opt-125m) model; [`unsloth/Llama-3.2-3b`](https://huggingface.co/unsloth/Llama-3.2-1B) model.
---
### Fine-Tuning Data

#### For `opt-125m` Model:
- **Dataset**:  
  We fetch the preprocessed dataset `fine_tuning_data_top_5000.jsonl`, which contains **5,000 records**, from the GCS bucket.
- **Data Split**:  
  90% of the fetched dataset is used for training, and 10% is used for validation.
- **Tokenization**:  
  The dataset is tokenized with the following parameters:
  - `max_length=512`
  - `truncation=True`
  - `padding='max_length'`

  Since we are using the `opt-125m` model as a Causal Language Model (CLM), both the recipe prompt and recipe steps are tokenized together as a single input to the model.

#### For `Llama` Model:
- **Dataset**:  
  We fetch the full-sized dataset, `fine_tuning_data.jsonl`, which contains **231,637 records**, from the GCS bucket.
- **Filtering**:  
  The dataset is filtered based on the following criteria:
  - **Prompt length**: ≤ 470 characters.
 <div style="display: flex; justify-content: space-between; align-items: center; gap: 20px;">
  <div style="flex: 1; text-align: center;">
    <p><strong>Before Filtering</strong></p>
    <img src="/screenshots/promptlength.png" alt="Distribution of Prompt Lengths Before Filtering" style="max-width: 100%; height: auto;"/>
  </div>
  <div style="flex: 1; text-align: center;">
    <p><strong>After Filtering</strong></p>
    <img src="/screenshots/promptlength_after.png" alt="Distribution of Prompt Lengths After Filtering" style="max-width: 100%; height: auto;"/>
  </div>
<div style="display: flex; justify-content: space-between; align-items: center; gap: 20px;">
  <div style="flex: 1; text-align: center;">
    <p><strong>Before Filtering</strong></p>
    <img src="/screenshots/completionlength.png" alt="Distribution of Prompt Lengths Before Filtering" style="max-width: 100%; height: auto;"/>
  </div>
  <div style="flex: 1; text-align: center;">
    <p><strong>After Filtering</strong></p>
    <img src="/screenshots/completionlength_after.png" alt="Distribution of Prompt Lengths After Filtering" style="max-width: 100%; height: auto;"/>
  </div>
</div>


  After filtering, the dataset contains **230,197 input-response pairs**.
- **Data Split**:  
  The filtered dataset is split into:
  - **Training set**: 80% of the filtered data.
  - **Validation set**: 20% of the filtered data.

- **Training Data Format**:
  Each record in the training dataset is structured as follows:
  1. **Task-specific instruction**:  
     `"Write a recipe that includes clear instructions and ingredients. Ensure the recipe has a detailed list of ingredients and step-by-step cooking instructions."`
  2. **Input prompt**:  
     The user-provided input to generate a recipe.
  3. **Expected response**:  
     The corresponding recipe, written step by step with detailed instructions.
  4. **EOS token**:  
     An end-of-sequence token appended to signify the end of the output.
---

### Fine-tuning choices
#### For `opt-125m` Model:
We train for 3 epochs with a learning rate of `5e-5`. The specific training parameters used in fine-tuning are as follows:
```
num_train_epochs=3,
per_device_train_batch_size=2,
gradient_accumulation_steps=4,
learning_rate=5e-5,
logging_dir="/app/logs",
logging_steps=10,
save_steps=50,
eval_strategy="steps",
eval_steps=50,
save_total_limit=1,
fp16=False,
max_grad_norm=0.3
```
We did not apply Parameter Efficient Fine-tuning (PEFT) such as LoRA for the fine-tuning task since LoRA works best for larger models, yet the `opt-125m` model is quite small. We plan on implementing LoRA for future milestones when we are able to finetune the model on GCP instead of locally.

#### For `Llama` Model with LoRA:
**Key Features**
- **LoRA-based parameter-efficient fine-tuning**:
  - Only specific low-rank layers are fine-tuned, drastically reducing the number of trainable parameters.
- **Gradient checkpointing**:
  - Reduces GPU memory usage by storing intermediate states during backpropagation.
- **2x faster fine-tuning and inference**:
  - Enabled through Unsloth's advanced optimizations, making the process efficient .
- **Automatic RoPE scaling**:
  - Allows the use of any `max_seq_length` dynamically by implementing Kaiokendev's RoPE scaling method.
- **4-bit quantization**:
  - Memory-efficient model loading using bits-and-bytes (bnb-4bit) quantization.
- **Monitor with W&B**

**LoRA Configurations**
- **Rank (`r`)**: `16`  
- **LoRA Alpha**: `16`  
- **LoRA Dropout**: `0` (dropout is disabled for LoRA layers to retain full training capacity.)
- **Bias**: `"none"`  (no additional bias terms are introduced.)
- **Target Modules**:  
  The LoRA adapters are applied to the following model layers:
  - `q_proj`, `k_proj`, `v_proj`
  - `up_proj`, `down_proj`, `o_proj`
  - `gate_proj`
- **RSLoRA**: Enabled (`use_rslora=True`)  to ensures stability during training by using Robust Scalable LoRA.
- **Gradient Checkpointing**: `"unsloth"`  (enables Unsloth's gradient checkpointing for memory efficiency)

**Hyperparameters and Other Model Configurations**
- **Learning Rate**: `3e-4`
- **Epochs**: `3`
- **Batch Size**: `4` (per device)
- **Optimizer**: `adamw_8bit`  (uses an 8-bit optimizer for efficient memory usage.)
- **Gradient Accumulation Steps**: `4`  (accumulates gradients across multiple steps to reduce memory load.)
- **Warmup Steps**: `10%` of total training steps.

**Finetune Instruction**
- We finetuned Llama use gup on GCP with nvidia-tesla-A100. One can run `/src/fine-tuning/llama/run.py` to initiate the finetuning process.

## LLM: RAG

- **Overview**: In this part, we implement the RAG workflow for generating recipes based on user queries.

- **Dataset**: The same preprocessed data is used for both finetuning task and RAG task. We first load the preprocessed data from the GCS bucket, then further processes and splits them into manageable chunks using `RecursiveCharacterTextSplitter` with `chunk_size=1000` and `chunk_overlap=200`.

- **Model Loading**: We load the `facebook/opt-125m` model with the `opt-125m` tokenizer.

- **RAG choices**: 
  - **Retriever**: We create retriever from the FAISS vector store (`vectorstore.as_retriever()`) and is configured to retrieve a specified number (`k=3`) of top relevant documents.
  The generator is set up through the Hugging Face pipeline (HuggingFacePipeline)
  - **Generator**: We set up the generator through the `HuggingFacePipeline` to generate the recipes based on the user queries.
  - **parameters**: 
    - `max_length=1024` gives a good balance between the length of the generated recipe and the memory usage.
    - `temperature=0.7` adds some randomness to the output without making it too chaotic.
    - `top_p=0.95` filters out less likely tokens.
    - `repetition_penalty=1.2` makes the model less likely to repeat itself.
    - `truncation=True` ensures that the generated text is not cut off abruptly.
    - `return_full_text=False` gives only the newly generated text.
    - `do_sample=True` allows the model to generate text in a more natural and creative way.
- **Example**:
   - query = "Please write a low-sodium meal recipe that takes approximately 55 minutes and includes the following ingredients: tomato, beef. The recipe should be formatted with a clear list of ingredients and cooking instructions."
   - One of the retrieved context: 
   ![image](./screenshots/llm-rag-example.png)

## APIs & Frontend Implementation

- **Overview**: The The ByteBites application consists of two main components: the frontend and the backend.  
- **Frontend**: This is the user interface of the application, built using Next.js. It includes the landing page and dashboard where users can upload grocery receipts, select ingredients, and generate personalized recipes. The frontend is located in the `landing/` directory. 
- **Backend**: This component handles the OCR & NER task, LLM task, and the Nutrition Extraction task. It processes uploaded receipt images to extract edible ingredient. Then it generates recipes based on the user's preferences and output the nutration facts based on selected ingredients. The backend is located in the `api-service/` directory and is built using FastAPI. 

### Setup Instructions

1. **Docker Compose**: 
   - You can use Docker Compose to set up both the frontend and backend services. Navigate to `src/`, and run the following command to start both services:
     ```bash
     docker-compose up --build
     ```
   - This will start the frontend on port 3000 and the backend on port 9000.

2. **Backend Setup**:
   - Navigate to the `api-service/` directory.
   - Build and run the Docker container using the provided shell script:
     ```bash
     sh docker-shell.sh
     ```
   - The backend service will be available at `http://localhost:9000`. You can access and try out the API endpoints at `http://localhost:9000/docs`.

3. **Frontend Setup**:
   - Navigate to the `landing/` directory.
   - Install the necessary dependencies:
     ```bash
     npm install
     ```
   - Start the development server:
     ```bash
     npm run dev
     ```
   - The frontend application will be available at `http://localhost:3000`.

### Usage Guidelines
- **Landing Page**: Access the landing page at `http://localhost:3000`. Here, you can see a landing page and learn about the features of ByteBites. After logging in, you can navigate to the dashboard.

   ![Landing Page](./screenshots/landing-page.png)

- **Dashboard**: On the dashboard, you can upload a grocery receipt to extract ingredients, select your meal preferences, and generate recipes.

   ![Dashboard](./screenshots/dashboard.png)
  
## Backend Implementation
We deploy and serve Llama on GCP with GPU acceleration (nvidia-tesla-p100) and a REST API interface.
- Below is a screenshot displaying the `health` route with external IP:
![image](./screenshots/ip_health.png)  

- Below is a screenshot displaying the `generate` route for generating recipes:
![image](./screenshots/llama_deploy.png)  

## CI & Testing

* note: `ocr-vm` and `llm-vm` folders are excluded because they are work-in-progress directories.

### Testing Tools Used
- **PyTest**: Used for running unit, integration, and system tests.
- **pytest-cov**: Used for generating code coverage reports.
- **Flake8**: Used for linting and code quality checks.

### Implemented Tests
#### Unit Tests
We test each functionality of our backend (in the `api-service` folder), including the `llm.py` router and the `ocr.py` router.
Please see the `test_llm.py` and `test_ocr.py` files in our `api-service/tests` directory. Please see the screenshot below for coverage:
![image](./screenshots/api-service-coverage.png)  


We also do an example unit test for one of our deprecated folders: **fine-tuning/**

We test the scripts `upload.py` and `inference_nutrition.py` only for this directory. The `upload.py` uploads our fine-tuned model to GCP, and the `inference_nutrition.py` file does inference with the fine-tuned model as well as generate nutrition facts. We have opted not to include tests for other scripts within this directory, as these scripts are either deprecated or were used exclusively for local fine-tuning tasks, which have already been completed and verified. Please see the screenshot below for coverage:

![image](./screenshots/fine-tuning-coverage.png)  

We are not including additional unit tests for other folders for the following reasons:
- **preprocessing/**: Already been completed and verified.
- **rag/**: We eliminated the use of rag in our project.
- **ocr/**: The ocr logic is already included in our backend as a router.
- **landing/**: It is the frontend of our app and only user inputs will be tested.

#### Integration Tests
We test how the different components in `service.py` work together, ensuring that interactions between modules, APIs, and dependencies are functioning correctly.
Please see the `test_service.py` file in our `api-service/tests` directory.

#### System Tests 
We use system tests to validate the behavior of user flow. We use OCR outputs as inputs to the LLM endpoint.
Please see the `test_service.py` file in our `api-service/tests` directory.

### Instructions to Run Tests Locally
1. First, navigate to the container directory you wish to test (e.g., `src/api-service`).
2. Next, run the following commands one by one
   ```
   # ensure `pipenv` is installed: 
   pip install pipenv

   # install dependencies
   pipenv install --dev

   # run the test with coverage report
   pipenv run pytest tests/ --cov=. --cov-report=term --cov-config=.coveragerc
   ```

## Deployment with Ansible

In this deployment approach, we deploy our web app using **only Ansible playbooks**. This deployment approach does not have Kubernetes and is for demonstration purposes only as requied by Milestone 5. For Kubernetes and Ansible deployment, please see [Deployment With Scaling Using Ansible and Kubernetes](#deployment-with-scaling-using-ansible-and-kubernetes).

#### Setup Instruction

> Reminder: You must ensure the `secrets/` folder at the location specied in [Directory Structure](#directory-structure) contains the `usda_api_key.env` file (key to USDA API, in a format like `USDA_API_KEY=...`, without quotation marks surrounding the API key content), the `recipe.json` file (which is the secrets for the GCP account storing the finetuned model safetensors), the `gcp-service.json` file (which is the secrets for the service account under the same project used for deployment), and the `deployment.json` file (which is responsible for Ansible deployment).
>
>> The service account `deployment` must have the following permissions
>>  - Compute Admin
>>  - Compute OS Login
>>  - Container Registry Service Agent
>>  - Kubernetes Engine Admin
>>  - Service Account User
>>  - Storage Admin
>>  - Artifact Registry Writer
>>  - Artifact Registry Reader
>> The service account `gcp-service` must have the following permissions
>>  - Storage Object Viewer
>>  - Artifact Registry Reader
>> You should create a gcr.io repository on GCP Artifact Registry

- Navigate to `src/deployment`
- Run `sh docker-shell.sh`
- SSH setup
  - Run `gcloud compute project-info add-metadata --project <YOUR GCP_PROJECT> --metadata enable-oslogin=TRUE`
  - Create SSH key for service account with
    ```
    cd /secrets
    ssh-keygen -f ssh-key-deployment
    cd /app
    ```
  - Providing public SSH keys to instances with `gcloud compute os-login ssh-keys add --key-file=/secrets/ssh-key-deployment.pub`
  - Change details in the `inventory.yml` file
    - Change `ansible_user` to the `username` gotten from the previous command output
    - Change `gcp_service_account_email` to the deployment@<MY_GCP_PROJECT_ID>.iam.gserviceaccount.com
    - Change `gcp_project` to your project id 
    - Change `gcp_region` and `gcp_zone` as needed
- Run `ansible-playbook deploy-docker-images.yml -i inventory.yml`. 
- Run `ansible-playbook deploy-create-instance.yml -i inventory.yml --extra-vars cluster_state=present` which creates the Virtual Machine
- Run `ansible-playbook deploy-provision-instance.yml -i inventory.yml` after changing details in the `inventory.yml` file
  - Change `appserver > hosts` to the external IP address of the VM
- Run `ansible-playbook deploy-setup-containers.yml -i inventory.yml`
- Run `ansible-playbook deploy-setup-webserver.yml -i inventory.yml` after changing details in the `nginx-conf/nginx/nginx.conf` file

**Our web app is deployed with these Ansible playbooks and ready to be viewed at http://34.68.205.67/**


## Deployment With Scaling Using Ansible and Kubernetes

In this deployment approach, we deploy our web app using **Kubernetes powered by Ansible playbooks**. We also implement manual scaling up and manual scaling down options.

**Our web app is currently deployed with Kubernetes and ready to be viewed at http://35.226.149.192.sslip.io**

#### Setup instructions

> Reminder: You must ensure the `secrets/` folder at the location specied in [Directory Structure](#directory-structure) contains the `usda_api_key.env` file (key to USDA API, in a format like `USDA_API_KEY=...`, without quotation marks surrounding the API key content), the `recipe.json` file (which is the secrets for the GCP account storing the finetuned model safetensors), the `gcp-service.json` file (which is the secrets for the service account under the same project used for deployment), and the `deployment.json` file (which is responsible for Ansible deployment).
>
>> The service account `deployment` must have the following permissions
>>  - Compute Admin
>>  - Compute OS Login
>>  - Container Registry Service Agent
>>  - Kubernetes Engine Admin
>>  - Service Account User
>>  - Storage Admin
>>  - Artifact Registry Writer
>>  - Artifact Registry Reader
>> The service account `gcp-service` must have the following permissions
>>  - Storage Object Viewer
>>  - Artifact Registry Reader
>> You should create a gcr.io repository on GCP Artifact Registry

- Navigate to `src/deployment`
- run `sh docker-shell.sh`
- Run `ansible-playbook deploy-docker-images.yml -i inventory.yml`, which creates and pushes the web app containers to GCP Artifact Registry
- Run `ansible-playbook deploy-k8s-cluster.yml -i inventory.yml --extra-vars cluster_state=present`, which deploys our web app on a Kubernetes cluster with NGINX ingress controller, and sets up the necessary GCP secrets and application credentials, and creates deployments and services for the API and frontend components in the specified namespace.
- You should be able to access the web app at http://<YOUR INGRESS IP>.sslip.io.
* note: if you exit the container and reenter again but kubectl gives a connection error, please run `gcloud container clusters get-credentials byte-bites-app-cluster --zone us-central1-a` to configure the cluster's credentials again.

#### Manual Scaling Up and Scaling Down
We added two separate plays in the `deploy-k8s-cluster.yml` playbook to enable manualing scaling our deployment up and down in order to handle increased or decreased load.
- After deploying as the above, i.e. without running the `deploy-k8s-cluster.yml` playbook with `scale-up` or `scale-down` arguments, we use a default of 1 replica:
  ![image](./screenshots/kubernetes_without_scaling.png)  
- When running the `deploy-k8s-cluster.yml` playbook again with `scale-up` argument, 
  ```
  ansible-playbook deploy-k8s-cluster.yml -i inventory.yml --tags scale-up
  ```
  The [Scale Up the Deployment] play will run, and we scale up to 5 replicas:
  ![image](./screenshots/kubernetes_scaled_up.png)  
- When running the `deploy-k8s-cluster.yml` playbook again with `scale-down` argument, 
  ```
  ansible-playbook deploy-k8s-cluster.yml -i inventory.yml --tags scale-down
  ```
  The [Scale Down the Deployment] play will run, and we scale down again to 1 replica:
  ![image](./screenshots/kubernetes_scaled_down.png)   

## Usage details and Examples

- Nagivate to http://35.226.149.192.sslip.io, you should see the landing page with a get started button: 
![image](./screenshots/landing.png)
- Click on the Get Started button
  - You can sign up with Google or your email if you're a new user.
  - You can also sign in with Google or your email if you're a returning user.
- After signing in, you should see the dashboard:
![image](./screenshots/dashboard.png)
- You can upload a grocery receipt by clicking on the Upload Receipt button.
![image](./screenshots/upload-receipt.png)
- Our app will automatically extract the ingredients from the receipt and display them in the ingredient list. You can also manually add ingredients to the list. Also, you can select the ingredients, your dietary preferences, meal type, and cooking time for the recipe you want to generate. Finally, you can click on the Get Recipe button to generate a recipe.
![image](./screenshots/select-ingredients.png)
- Our app will generate a recipe based on users' preferences and you can view the nutrition analysis of the recipe by clicking on the Show Nutrition Analysis button.
![image](./screenshots/recipe.png)
- Nutrition analysis of the recipe will be displayed as follows. You can search for the nutrients of interest by typing in the search bar. Also, you can click on the Start Over button to start a new recipe generation.
![image](./screenshots/nutrition-analysis.png)
