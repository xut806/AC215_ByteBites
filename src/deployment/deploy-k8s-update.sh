ansible-playbook deploy-docker-images.yml -i inventory.yml -vv
ansible-playbook update-k8s-cluster.yml -i inventory-prod.yml -vv
