from fastapi.openapi.utils import get_openapi
from fastapi import FastAPI

def custom_openapi(app: FastAPI):
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="RAG API Documentation",
        version="1.0.0",
        description="""
        This API provides comprehensive endpoints for RAG (Retrieval-Augmented Generation) operations.
        
        ## Core Features
        * **Document Management**: Upload, download, and manage documents with automatic deduplication
        * **Vector Search**: Advanced similarity search with metadata filtering capabilities
        * **RAG Chat**: OpenAI-powered chat with document context retrieval
        * **Model Management**: Ollama model operations including search, pull, and status monitoring
        * **Collection Management**: Qdrant vector database collection operations
        * **Background Processing**: Asynchronous document processing with job tracking
        * **Metadata Analytics**: Collection statistics and document insights
        
        ## Key Endpoints
        * **Health**: System status and service connectivity checks
        * **Files**: Upload, download, delete, and list uploaded documents
        * **Search**: Basic and advanced vector similarity search with filtering
        * **Chat**: OpenAI chat with optional RAG document context
        * **Models**: Ollama model search, pull, and management
        * **Collections**: Qdrant collection creation and management
        * **Jobs**: Background job status monitoring
        * **Metadata**: Collection statistics and analytics
        
        ## Authentication
        Currently, this API does not require authentication.
        """,
        routes=app.routes,
    )

    openapi_schema["tags"] = [
        {
            "name": "Health",
            "description": "Health check and system status endpoints"
        },
        {
            "name": "Collections",
            "description": "Manage vector collections in Qdrant"
        },
        {
            "name": "Models",
            "description": "Manage and interact with LLM models via Ollama"
        },
        {
            "name": "Files",
            "description": "File upload, download, and management operations"
        },
        {
            "name": "Search",
            "description": "Vector similarity search and advanced search operations"
        },
        {
            "name": "Metadata",
            "description": "Collection metadata and statistics"
        },
        {
            "name": "Chat",
            "description": "OpenAI chat operations with RAG support"
        },
        {
            "name": "Jobs",
            "description": "Background job status and monitoring"
        }
    ]

    app.openapi_schema = openapi_schema
    return app.openapi_schema 