#!/bin/bash

# Quick start script for local development

echo "Starting Product Importer Application..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running. Please start Docker and try again."
    exit 1
fi

# Start services with Docker Compose
echo "Starting services with Docker Compose..."
docker-compose up --build

