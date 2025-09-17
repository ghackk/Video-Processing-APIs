#!/bin/bash

# Deployment script for Dripple Video Processing Backend
# Usage: ./scripts/deploy.sh [environment] [cloud_provider]

set -e

ENVIRONMENT=${1:-development}
CLOUD_PROVIDER=${2:-local}

echo "🚀 Deploying Dripple Video Processing Backend"
echo "Environment: $ENVIRONMENT"
echo "Cloud Provider: $CLOUD_PROVIDER"

# Function to deploy to AWS
deploy_aws() {
    echo "📦 Deploying to AWS..."
    
    # Check if AWS CLI is installed
    if ! command -v aws &> /dev/null; then
        echo "❌ AWS CLI not found. Please install AWS CLI first."
        exit 1
    fi
    
    # Build and push Docker image to ECR
    echo "🏗️ Building Docker image..."
    docker build -t dripple-backend .
    
    # Tag for ECR
    ECR_REPO="your-account.dkr.ecr.region.amazonaws.com/dripple-backend"
    docker tag dripple-backend:latest $ECR_REPO:latest
    
    # Push to ECR
    echo "📤 Pushing to ECR..."
    aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $ECR_REPO
    docker push $ECR_REPO:latest
    
    # Deploy to ECS
    echo "🚀 Deploying to ECS..."
    aws ecs update-service --cluster dripple-cluster --service dripple-service --force-new-deployment
    
    echo "✅ Deployment to AWS completed!"
}

# Function to deploy to GCP
deploy_gcp() {
    echo "📦 Deploying to GCP..."
    
    # Check if gcloud CLI is installed
    if ! command -v gcloud &> /dev/null; then
        echo "❌ gcloud CLI not found. Please install Google Cloud SDK first."
        exit 1
    fi
    
    # Build and push to Google Container Registry
    echo "🏗️ Building and pushing to GCR..."
    gcloud builds submit --tag gcr.io/your-project/dripple-backend .
    
    # Deploy to Cloud Run
    echo "🚀 Deploying to Cloud Run..."
    gcloud run deploy dripple-backend \
        --image gcr.io/your-project/dripple-backend \
        --platform managed \
        --region us-central1 \
        --allow-unauthenticated
    
    echo "✅ Deployment to GCP completed!"
}

# Function to deploy to Azure
deploy_azure() {
    echo "📦 Deploying to Azure..."
    
    # Check if Azure CLI is installed
    if ! command -v az &> /dev/null; then
        echo "❌ Azure CLI not found. Please install Azure CLI first."
        exit 1
    fi
    
    # Build and push to Azure Container Registry
    echo "🏗️ Building and pushing to ACR..."
    az acr build --registry your-registry --image dripple-backend .
    
    # Deploy to Container Instances
    echo "🚀 Deploying to Container Instances..."
    az container create \
        --resource-group your-resource-group \
        --name dripple-backend \
        --image your-registry.azurecr.io/dripple-backend:latest \
        --ports 8000 \
        --environment-variables \
            DATABASE_URL=postgresql://user:pass@host:5432/db \
            REDIS_URL=redis://host:6379/0
    
    echo "✅ Deployment to Azure completed!"
}

# Function to deploy locally with Docker Compose
deploy_local() {
    echo "📦 Deploying locally with Docker Compose..."
    
    # Stop existing containers
    docker-compose down
    
    # Build and start services
    docker-compose up --build -d
    
    # Wait for services to be healthy
    echo "⏳ Waiting for services to be healthy..."
    sleep 30
    
    # Check health
    if curl -f http://localhost:8000/health; then
        echo "✅ Local deployment completed and healthy!"
    else
        echo "❌ Health check failed!"
        exit 1
    fi
}

# Main deployment logic
case $CLOUD_PROVIDER in
    "aws")
        deploy_aws
        ;;
    "gcp")
        deploy_gcp
        ;;
    "azure")
        deploy_azure
        ;;
    "local")
        deploy_local
        ;;
    *)
        echo "❌ Unknown cloud provider: $CLOUD_PROVIDER"
        echo "Supported providers: aws, gcp, azure, local"
        exit 1
        ;;
esac

echo "🎉 Deployment completed successfully!"
