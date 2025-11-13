@echo off
REM Quick start script for Windows

echo Starting Product Importer Application...

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo Error: Docker is not running. Please start Docker and try again.
    exit /b 1
)

REM Start services with Docker Compose
echo Starting services with Docker Compose...
docker-compose up --build

