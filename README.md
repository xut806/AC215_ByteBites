# ByteBites: Recipe Generation

## Directory Structure

Our repo is structured as follows:

```
├── preprocessing/          # Preprocessing raw recipe data from a Google Cloud Storage bucket and prepare it for fine-tuning.        
│   ├── data_preprocessing.py    
│   ├── docker-shell.sh   
│   ├── docker-entrypoint.sh  
│   ├── Dockerfile   
│   ├── Pipfile   
│   └── Pipfile.lock
│
├── reports/                 # Application mock-up and interactive prototype
│   ├── AC215_webapp_prototype.pdf          
│   └── prototype_link.md
│
├── fine-tuning/             # Fine-tuning LLM using the preprocessed recipe data.
│   ├── utils.py   
│   ├── fine_tune.py    
│   ├── compare_models.py   
│   ├── docker-shell.sh   
│   ├── docker-entrypoint.sh  
│   ├── Dockerfile   
│   ├── Pipfile   
│   └── Pipfile.lock
│
├── rag/                     # Implementing RAG workflow for generating recipes based on user queries
│   ├── rag.py   
│   ├── docker-shell.sh   
│   ├── docker-entrypoint.sh  
│   ├── Dockerfile   
│   ├── Pipfile   
│   └── Pipfile.lock
├── .env
├── .gitignore
├── README.md
├── LICENSE
```

Please make sure to create an `.env` file in the location as shown above after cloning the repo.

## Containers

We have three containers for this project and each container serves a specific purpose within the project, including data preprocessing, fine-tuning, and RAG (Retrieval-Augmented Generation).

### Container 1: Data Preprocessing

- **Purpose**: To process raw recipe data from a Google Cloud Storage bucket and prepare it for fine-tuning.

- **Files**:
  - `Dockerfile`: Defines the environment and dependencies for data preprocessing.
  - `Pipfile`: Manages Python packages.
  - `data_preprocessing.py`: Contains the preprocessing logic, where we fetch the data from the Google Cloud Storage bucket and upload the processed data to Google Cloud Storage for the next container.
  - `docker-entrypoint.sh`: Entry point script for the container.

- **Instructions**: 
  - In the `/preprocessing` directory, run `sh docker-shell.sh` to start the container.
  - Once the container is running, run `python data_preprocessing.py` to start the data preprocessing.

### Container 2: Fine-Tuning

- **Purpose**: To fine-tune the language model using the preprocessed recipe data.

- **Files**:
  - `Dockerfile`: Sets up the environment for fine-tuning.
  - `Pipfile`: Manages Python packages.
  - `fine_tune.py`: Contains the fine-tuning logic.
  - `utils.py`: Contains the utility functions for fine-tuning.
  - `docker-entrypoint.sh`: Entry point script for the container.
  - `compare_models.py`: Contains the logic to compare the performance of the fine-tuned model with the base model.

- **Instructions**:
  - In the `/fine-tuning` directory, run `sh docker-shell.sh` to start the container.
  - Once the container is running, run `python fine_tune.py` to start the fine-tuning. You may choose not to run this step, because we have already fine-tuned and copied the model to the container. (However, due to the size of the model, we did not push it to Github.)
  - You can run `python compare_models.py` to compare the performance of the fine-tuned model with the base model.

### Container 3: RAG (Retrieval-Augmented Generation)

- **Purpose**: To implement the RAG workflow for generating recipes based on user queries.

- **Files**:
  - Dockerfile: Defines the environment for the RAG server.
  - Pipfile: Manages Python packages.
  - rag.py: Contains the RAG implementation.
  - docker-entrypoint.sh: Entry point script for the container.

- **Instructions**:
  - In the `/rag` directory, run `sh docker-shell.sh` to start the container.
  - Once the container is running, run `python rag.py` to start the RAG server and see the results.
