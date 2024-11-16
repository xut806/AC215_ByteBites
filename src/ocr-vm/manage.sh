#!/bin/sh

# Load environment variables from .env file
set -o allexport
source ./.env
set +o allexport

# Usage function to display help
usage() {
    echo "Usage: $0 {build|deploy|create-service-account|connect|clean|teardown|update}"
    echo "Commands:"
    echo "  build                 - Build the Docker image using Cloud Build"
    echo "  deploy                - Deploy the Docker image to a VM instance"
    echo "  create-service-account - Set up a service account with necessary roles"
    echo "  connect               - SSH into running VM"
    echo "  update                - Update VM to run most recent container"
    echo "  clean                 - Clean up old images and cache to free up space"
    echo "  teardown              - Remove all provisioned resources"
    exit 1
}

# Check if command argument is provided
if [ -z "$1" ]; then
    usage
fi
deploy() {
    echo "Setting up service account..."
    SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
    VM_TAG="allow-http-${INSTANCE_NAME}"

    # Create service account if it doesn't exist
    if ! gcloud iam service-accounts describe "$SA_EMAIL" >/dev/null 2>&1; then
        echo "Creating service account..."
        gcloud iam service-accounts create "$SA_NAME" \
            --display-name="OCR NER Service Account" \
            --quiet
    fi

    # Grant necessary permissions
    echo "Granting required roles to service account..."
    gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
        --member="serviceAccount:${SA_EMAIL}" \
        --role="roles/artifactregistry.reader" \
        --quiet > /dev/null

    gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
        --member="serviceAccount:${SA_EMAIL}" \
        --role="roles/storage.admin" \
        --quiet > /dev/null

    # Deploy VM instance without GPU
    echo "Deploying VM instance..."
    gcloud compute instances create ${INSTANCE_NAME} \
        --project=${PROJECT_ID} \
        --zone=${ZONE} \
        --machine-type="e2-medium" \
        --service-account="${SA_EMAIL}" \
        --scopes="https://www.googleapis.com/auth/cloud-platform" \
        --image-family=ubuntu-2204-lts \
        --image-project=ubuntu-os-cloud \
        --boot-disk-size=${DISK_SIZE} \
        --metadata-from-file=user-data=cloud-init.yaml \
        --tags=${VM_TAG}

    # Create firewall rule if it doesn't exist
    if ! gcloud compute firewall-rules describe allow-http-${INSTANCE_NAME} --project=${PROJECT_ID} >/dev/null 2>&1; then
        echo "Creating firewall rule..."
        gcloud compute firewall-rules create allow-http-${INSTANCE_NAME} \
            --allow=tcp:${PORT} \
            --target-tags=${VM_TAG} \
            --description="Allow HTTP traffic on port ${PORT} for ${INSTANCE_NAME}" \
            --quiet
    fi
}



# Other functions (build, clean, teardown, create-service-account, update_container)
connect() {
    echo "SSHing into VM..."
    gcloud compute ssh ${INSTANCE_NAME} --zone=${ZONE}
}

build() {
    echo "Building and pushing Docker image..."
    
    # Ensure the repository exists (will be created if it doesn't)
    gcloud artifacts repositories describe ${REPO_NAME} \
        --location=${REGION} >/dev/null 2>&1 || \
    gcloud artifacts repositories create ${REPO_NAME} \
        --repository-format=docker \
        --location=${REGION} \
        --quiet

    # Submit build
    gcloud builds submit --config=cloudbuild.yaml
}

clean() {
    echo "Cleaning up Cloud Build and Docker caches..."

    # Cancel any ongoing builds and remove outdated Docker images
    gcloud builds list --format="value(id)" | while read -r build_id; do
        gcloud builds cancel "$build_id"
    done

    # Delete images older than a set period (e.g., 7 days)
    gcloud container images list-tags "$IMAGE_NAME" --filter="timestamp.datetime < '-7d'" --format="get(digest)" | while read -r digest; do
        gcloud container images delete "$IMAGE_NAME@$digest" --quiet --force-delete-tags
    done
}

update_container() {
    echo "Updating container on VM instance..."
    gcloud compute instances update-container ${INSTANCE_NAME} \
        --zone=${ZONE} \
        --container-image="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${IMAGE_NAME}:latest" \
        --container-env="MODEL_ID=${MODEL_ID},PROJECT_ID=${PROJECT_ID},BUCKET_NAME=${BUCKET_NAME},CACHE_DIR=/mnt/disks/model-cache"
}

teardown() {
    echo "Tearing down resources..."

    # Remove the VM instance
    echo "Removing VM instance..."
    gcloud compute instances delete "$INSTANCE_NAME" --zone "$ZONE" --quiet

    # Delete firewall rule
    echo "Removing firewall rule..."
    gcloud compute firewall-rules delete "allow-http-${INSTANCE_NAME}" --quiet

    # Delete runtime service account
    echo "Removing runtime service account..."
    SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
    gcloud iam service-accounts delete "$SA_EMAIL" --quiet

    # Delete build service account
    echo "Removing build service account..."
    BUILD_SA_NAME="llm-build-sa"
    BUILD_SA_EMAIL="${BUILD_SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
    gcloud iam service-accounts delete "$BUILD_SA_EMAIL" --quiet

    # Optionally delete the persistent disk (comment out to preserve cache)
    # echo "Removing persistent disk..."
    # gcloud compute disks delete "${DISK_NAME}" --zone "${ZONE}" --quiet

    echo "Teardown complete."
}

# Execute the specified command
case "$1" in
    build)
        build
        ;;
    deploy)
        deploy
        ;;
    create-service-account)
        create-service-account
        ;;
    connect)
        connect
        ;;
    clean)
        clean
        ;;
    update)
        update_container
        ;;
    teardown)
        teardown
        ;;
    *)
        usage
        ;;
esac

