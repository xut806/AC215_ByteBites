#!/bin/bash
set -x  # Enable debug mode

echo "=== Starting deployment process ==="

echo "=== Running deploy-docker-images playbook ==="
ansible-playbook -vv deploy-docker-images.yml -i inventory.yml

echo "=== Checking generated docker tag ==="
cat .docker-tag
NEW_TAG=$(cat .docker-tag)

echo "=== Verifying images in GCR ==="
gcloud container images list-tags gcr.io/ac215-project-434717/bytebites-frontend --limit=3 --sort-by=~timestamp

echo "=== Running update-k8s-cluster playbook ==="
ansible-playbook -vv update-k8s-cluster.yml -i inventory-prod.yml

echo "=== Force updating deployment with new image ==="
kubectl set image deployment/frontend frontend=gcr.io/ac215-project-434717/bytebites-frontend:${NEW_TAG} -n byte-bites-app-cluster-namespace

echo "=== Verifying Kubernetes Deployment ==="
kubectl get deployment frontend -n byte-bites-app-cluster-namespace -o jsonpath='{.spec.template.spec.containers[0].image}'
echo ""
kubectl get pods -n byte-bites-app-cluster-namespace
