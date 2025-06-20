source .env

aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin $AWS_ECR_REGISTRY
docker build -t $IMAGE_NAME . --platform "linux/amd64" --provenance false
docker tag $IMAGE_NAME:latest $ECR_IMAGE_URI
docker push $ECR_IMAGE_URI