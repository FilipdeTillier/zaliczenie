```
rag-app/
├── app.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── setup.sh
└── README.md
```

2. **Make the setup script executable:**

```bash
chmod +x setup.sh
```

3. **Run the setup script:**

```bash
./setup.sh
```

The script will:

- Start all the services
- Pull the deepseek-r1:7b model
- Provide status information

## Manual Setup

If you prefer to set up manually:

1. **Start the services:**

```bash
docker-compose up -d
```

2. **Pull the LLM model:**

```bash
curl -X POST http://localhost:11434/api/pull -d '{"name": "deepseek-r1:7b"}'
```

3. **Monitor the model download:**

```bash
curl http://localhost:11434/api/status
```

## Available Endpoints

Once the application is running, you can access the following endpoints:

- `GET /health` - Check the health of all services
- `GET /collections` - List all collections in Qdrant
- `POST /collections` - Create a new collection
- `GET /models` - List available models in Ollama
- `POST /embeddings` - Generate embeddings for text
- `POST /documents` - Index documents into a collection
- `POST /search` - Search for similar documents
- `POST /query` - Query the LLM (with or without RAG)
- `POST /pull_model` - Pull a model in the background
- `GET /model_status` - Check model download status

## Example Usage

### Create a collection:

```bash
curl -X POST http://localhost:8080/collections \
  -H "Content-Type: application/json" \
  -d '{"name": "my_documents", "vector_size": 1024}'
```

### Index a document:

```bash
curl -X POST "http://localhost:8080/documents?collection_name=my_documents" \
  -H "Content-Type: application/json" \
  -d '{"text": "Retrieval-Augmented Generation (RAG) is a technique that enhances large language model outputs by retrieving relevant information from external knowledge sources."}'
```

### Search for documents:

```bash
curl -X POST http://localhost:8080/search \
  -H "Content-Type: application/json" \
  -d '{"query": "What is RAG?", "collection_name": "my_documents"}'
```

### Query with RAG:

```bash
curl -X POST http://localhost:8080/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Explain RAG to me", "use_rag": true, "collection_name": "my_documents"}'
```

## Stopping the Application

To stop all services:

```bash
docker-compose down
```

To completely remove all data (including the downloaded model):

```bash
docker-compose down -v
```

## Troubleshooting

- If you encounter memory issues, try increasing the memory allocation in Docker's settings
- Check service logs: `docker-compose logs [service_name]`
- For model issues: `docker-compose logs ollama`
- For API issues: `docker-compose logs backend`
