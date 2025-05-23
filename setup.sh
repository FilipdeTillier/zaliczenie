#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Setting up RAG application...${NC}"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
  echo -e "${RED}Error: Docker is not running. Please start Docker and try again.${NC}"
  exit 1
fi

# Create directory structure if it doesn't exist
echo -e "${YELLOW}Ensuring all files are in the correct location...${NC}"

# Start the containers
echo -e "${YELLOW}Starting containers...${NC}"
docker-compose up -d

# Wait for services to be ready
echo -e "${YELLOW}Waiting for services to start...${NC}"
sleep 10

# Check if Ollama is up
echo -e "${YELLOW}Checking if Ollama service is ready...${NC}"
RETRIES=0
MAX_RETRIES=30
OLLAMA_READY=false

while [ $RETRIES -lt $MAX_RETRIES ] && [ "$OLLAMA_READY" = false ]; do
  if curl -s http://localhost:11434/api/tags > /dev/null; then
    OLLAMA_READY=true
    echo -e "${GREEN}Ollama service is ready!${NC}"
  else
    echo -e "${YELLOW}Waiting for Ollama service to be ready... (Attempt $((RETRIES+1))/$MAX_RETRIES)${NC}"
    sleep 5
    RETRIES=$((RETRIES+1))
  fi
done

if [ "$OLLAMA_READY" = false ]; then
  echo -e "${RED}Ollama service failed to start in a reasonable time.${NC}"
  echo -e "${YELLOW}Please check logs with: docker-compose logs ollama${NC}"
  exit 1
fi

# Pull the model
echo -e "${YELLOW}Pulling the deepseek-r1:7b model (this may take some time)...${NC}"
curl -X POST http://localhost:11434/api/pull -d '{"name": "deepseek-r1:7b"}'

echo -e "${GREEN}Setup complete! Your RAG application is now running.${NC}"
echo -e "${YELLOW}Qdrant is available at: http://localhost:6333${NC}"
echo -e "${YELLOW}Ollama is available at: http://localhost:11434${NC}"
echo -e "${YELLOW}Backend API is available at: http://localhost:8080${NC}"
echo ""
echo -e "${YELLOW}To check the API health: http://localhost:8080/health${NC}"
echo -e "${YELLOW}To check Ollama models: http://localhost:8080/models${NC}"
echo -e "${YELLOW}To monitor model download: http://localhost:8080/model_status${NC}"
echo ""
echo -e "${YELLOW}To stop the services: docker-compose down${NC}"