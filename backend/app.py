import os
from services.qdrantService import QdrantService
from fastapi import FastAPI, HTTPException, Body, Query, UploadFile, File 
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from typing import List
from qdrant_client import QdrantClient
from dotenv import load_dotenv
import httpx
from models.collection import Collection
from models.document import Document
from models.embedding_request import EmbeddingRequest
from models.model_pull_request import ModelPullRequest
from models.query_request import QueryRequest
from models.search_query import SearchQuery
from services.openAiService import OpenAIService
from swagger_config import custom_openapi
from services.ollamaService import OllamaService
from services.openAiService import OpenAIService
from models.openai_response import OpenAIChatRequest
from fastapi.responses import StreamingResponse
from controllers.qdrant_controller import router as vector_database_controller
from controllers.config_controller import router as config_controller
from controllers.ollama_controller import router as ollama_controller
from services.fileService import files_service


QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "rag_collection")

load_dotenv()

app = FastAPI(
    title="RAG API",
    description="API for Retrieval-Augmented Generation operations",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

app.include_router(vector_database_controller)
app.include_router(config_controller)
app.include_router(ollama_controller)

app.openapi = lambda: custom_openapi(app)

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
qdrant_service = QdrantService(host=qdrant_host, port=qdrant_port)

# Configure Ollama
ollama_host = os.getenv("OLLAMA_HOST", "localhost")
ollama_port = os.getenv("OLLAMA_PORT", "11434")
OLLAMA_BASE_URL = f"http://{ollama_host}:{ollama_port}"
MODEL_NAME_VAL = os.getenv("MODEL_NAME_VAL", "deepseek-r1:8b")

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
    """Pull a model with timeout handling"""
    try:
        async with httpx.AsyncClient(timeout=300.0) as client:  # 5 minutes timeout
            response = await client.post(
                f"{OLLAMA_BASE_URL}/api/pull",
                json={"name": MODEL_NAME_VAL}
            )
            if response.status_code != 200:
                print(f"Failed to pull model {MODEL_NAME_VAL}: {response.text}")
                return False
            return True
    except httpx.TimeoutException:
        print(f"Timeout while pulling model {MODEL_NAME_VAL}")
        return False
    except Exception as e:
        print(f"Error pulling model {MODEL_NAME_VAL}: {str(e)}")
        return False

@app.post("/post_documents", tags=["Files"])
async def post_documents(files: List[UploadFile] = File(...)):
    """
    Accepts multiple files and saves them to the 'backend/files' directory with random names.
    """
    if not files or len(files) == 0:
        raise HTTPException(status_code=400, detail="No files provided.")
    saved_files = []
    try:
        for file in files:
            random_filename = file.filename
            file.filename = random_filename
        saved_files = await files_service.save_files(files)
        return {"status": "success", "saved_files": saved_files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving files: {str(e)}")


# @app.post("/embeddings", tags=["Documents"])
# async def get_embeddings_for_text(request: EmbeddingRequest):
#     """
#     Generate embeddings for the provided text.
    
#     Args:
#         request: Text to generate embeddings for
        
#     Returns:
#         Generated embedding vector and its dimensions
#     """
#     try:
#         embedding = await generate_embedding(request.text)
#         return {"embedding": embedding, "dimensions": len(embedding)}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to generate embeddings: {str(e)}")

# @app.post("/documents", tags=["Documents"])
# async def index_document(document: Document, collection_name: str):
#     """
#     Index a document in the specified collection.
    
#     Args:
#         document: Document to index
#         collection_name: Name of the collection to index in
        
#     Returns:
#         Success message
#     """
#     try:
#         # Generate embedding for the document
#         embedding = await generate_embedding(document.text)
        
#         # Add to Qdrant
#         qdrant_client.upsert(
#             collection_name=collection_name,
#             points=[{
#                 "id": str(int(time.time() * 1000)),  # Use timestamp as ID
#                 "vector": embedding,
#                 "payload": {
#                     "text": document.text,
#                     **({} if document.metadata is None else document.metadata)
#                 }
#             }]
#         )
        
#         return {"status": "success", "message": "Document indexed successfully"}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to index document: {str(e)}")

@app.post("/search", tags=["Search"])
async def search_documents(query: SearchQuery):
    """
    Search for similar documents in a collection.
    
    Args:
        query: Search query configuration
        
    Returns:
        List of similar documents with scores
    """
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

@app.post("/query", tags=["Search"])
async def query_endpoint(request: QueryRequest):
    """
    Query the LLM with optional RAG context.
    
    Args:
        request: Query configuration including messages and RAG settings
        
    Returns:
        LLM response and source documents (if RAG is enabled)
    """
    try:
        if not request.use_rag:
            if request.use_local:
                ollama_service = OllamaService()
                response = await ollama_service.query_model(request.query)
            else:    
                openai_service = OpenAIService()
                response = await openai_service.query_model(messages=request.query.messages, model=request.query.model)
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
        print(e)
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

@app.post("/open_ai/chat")
async def open_ai_chat(request: OpenAIChatRequest):

    openAiService = OpenAIService()

    try:
        # Assuming openAiService is available in the scope
        response = await openAiService.query_model(
            model=request.model,
            messages=[message.dict() for message in request.messages]
        )
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI chat failed: {str(e)}")



if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=True)