import os
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from qdrant_client import QdrantClient
from dotenv import load_dotenv
import httpx
import time
import json
from models.collection import Collection
from models.document import Document
from models.embedding_request import EmbeddingRequest
from models.model_pull_request import ModelPullRequest
from models.query_request import QueryRequest
from models.search_query import SearchQuery
from services.openAiService import OpenAIService

# Load environment variables
load_dotenv()

app = FastAPI(title="RAG API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect to Qdrant
qdrant_host = os.getenv("QDRANT_HOST", "localhost")
qdrant_port = int(os.getenv("QDRANT_PORT", 6333))
qdrant_client = QdrantClient(host=qdrant_host, port=qdrant_port)

# Configure Ollama
ollama_host = os.getenv("OLLAMA_HOST", "localhost")
ollama_port = os.getenv("OLLAMA_PORT", "11434")
OLLAMA_BASE_URL = f"http://{ollama_host}:{ollama_port}"
MODEL_NAME_VAL = os.getenv("MODEL_NAME_VAL", "deepseek-r1:7b")

# Helper functions
async def generate_embedding(text: str):
    """Generate embedding using Ollama API"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{OLLAMA_BASE_URL}/api/embeddings",
            json={"model": MODEL_NAME_VAL, "prompt": text}
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, 
                               detail=f"Failed to generate embedding: {response.text}")
        return response.json()["embedding"]

async def query_llm(prompt: object):
    """Query the LLM directly using Ollama API"""
    print(f"Query prompt: {prompt.json()}")
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json=prompt.json(),
            timeout=120,
        )

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, 
                               detail=f"Failed to query LLM: {response.text}")
        
        return response.json()

async def pull_model(MODEL_NAME_VAL: str = MODEL_NAME_VAL):
    """Pull a model in the background"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{OLLAMA_BASE_URL}/api/pull",
            json={"name": MODEL_NAME_VAL}
        )
        if response.status_code != 200:
            print(f"Failed to pull model {MODEL_NAME_VAL}: {response.text}")
            return False
        return True

# Endpoints
@app.get("/")
async def root():
    return {"message": "Welcome to the RAG API", "model": MODEL_NAME_VAL}

@app.get("/health")
async def health():
    try:
        # Check if Qdrant is reachable
        qdrant_collections = qdrant_client.get_collections()
        
        # Check if Ollama is reachable
        ollama_status = {"status": "unknown"}
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
                if resp.status_code == 200:
                    ollama_status = {"status": "connected", "models": [m["name"] for m in resp.json().get("models", [])]}
                else:
                    ollama_status = {"status": "error", "details": resp.text}
        except Exception as e:
            ollama_status = {"status": "error", "details": str(e)}
        
        return {
            "status": "healthy" if ollama_status["status"] == "connected" else "degraded", 
            "qdrant": {"status": "connected", "collections": len(qdrant_collections.collections)},
            "ollama": ollama_status
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

@app.get("/collections")
async def get_collections():
    try:
        collections = qdrant_client.get_collections()
        return {"collections": [c.name for c in collections.collections]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get collections: {str(e)}")

@app.post("/collections")
async def create_collection(collection: Collection):
    try:
        qdrant_client.create_collection(
            collection_name=collection.name,
            vectors_config={
                "size": collection.vector_size,
                "distance": collection.distance,
            }
        )
        return {"status": "success", "message": f"Collection {collection.name} created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create collection: {str(e)}")

@app.get("/models")
async def get_models():
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            if resp.status_code == 200:
                models = resp.json()
                return {"models": models.get("models", [])}
            else:
                raise HTTPException(status_code=resp.status_code, detail="Failed to get models from Ollama")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get models: {str(e)}")

@app.post("/pull_model")
async def start_model_pull(request: ModelPullRequest, background_tasks: BackgroundTasks):
    MODEL_NAME_VAL = request.MODEL_NAME_VAL or MODEL_NAME_VAL
    background_tasks.add_task(pull_model, MODEL_NAME_VAL)
    return {"status": "success", "message": f"Started pulling model {MODEL_NAME_VAL}"}

@app.get("/model_status")
async def model_status():
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{OLLAMA_BASE_URL}/api/status")
            if resp.status_code == 200:
                return resp.json()
            else:
                return {"status": "unknown"}
    except Exception:
        return {"status": "unknown"}

@app.post("/embeddings")
async def get_embeddings_for_text(request: EmbeddingRequest):
    try:
        embedding = await generate_embedding(request.text)
        return {"embedding": embedding, "dimensions": len(embedding)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate embeddings: {str(e)}")

@app.post("/documents")
async def index_document(document: Document, collection_name: str):
    try:
        # Generate embedding for the document
        embedding = await generate_embedding(document.text)
        
        # Add to Qdrant
        qdrant_client.upsert(
            collection_name=collection_name,
            points=[{
                "id": str(int(time.time() * 1000)),  # Use timestamp as ID
                "vector": embedding,
                "payload": {
                    "text": document.text,
                    **({} if document.metadata is None else document.metadata)
                }
            }]
        )
        
        return {"status": "success", "message": "Document indexed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to index document: {str(e)}")

@app.post("/search")
async def search_documents(query: SearchQuery):
    try:
        # Generate embedding for query
        query_embedding = await generate_embedding(query.query)
        
        # Search in Qdrant
        search_results = qdrant_client.search(
            collection_name=query.collection_name,
            query_vector=query_embedding,
            limit=query.top_k
        )
        
        # Format results
        results = [
            {
                "score": hit.score,
                "text": hit.payload.get("text", ""),
                "metadata": {k: v for k, v in hit.payload.items() if k != "text"}
            } 
            for hit in search_results
        ]
        
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.post("/query")
async def query_endpoint(request: QueryRequest):
    print(f"Query request: {request}")
    try:
        if not request.use_rag:
            # Direct LLM query without RAG
            openai_service = OpenAIService()
            response = await openai_service.query_model(messages=request.query.messages, model=request.query.model)
            # response = await query_llm(request.query)
            return {"response": response, "source_documents": []}
        else:
            # RAG query
            if not request.collection_name:
                raise HTTPException(status_code=400, detail="Collection name is required for RAG queries")
            
            # 1. Convert query to embedding
            query_embedding = await generate_embedding(request.query)
            
            # 2. Search for similar documents
            search_results = qdrant_client.search(
                collection_name=request.collection_name,
                query_vector=query_embedding,
                limit=5
            )
            
            # 3. Format source documents
            sources = [
                {
                    "text": hit.payload.get("text", ""),
                    "score": hit.score,
                    "metadata": {k: v for k, v in hit.payload.items() if k != "text"}
                } 
                for hit in search_results
            ]
            
            # 4. Create prompt with context
            context = "\n\n".join([f"Document {i+1}:\n{doc['text']}" for i, doc in enumerate(sources)])
            
            prompt = f"""Answer the question based on the provided context.
            
                Context:
                {context}

                Question: {request.query}

                Answer:"""
            
            # 5. Query LLM with RAG context
            response = await query_llm(prompt)
            
            return {
                "response": response,
                "source_documents": sources
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=True)