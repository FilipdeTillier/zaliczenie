from fastapi.openapi.utils import get_openapi
from fastapi import FastAPI

def custom_openapi(app: FastAPI):
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="RAG API Documentation",
        version="1.0.0",
        description="""
        This API provides endpoints for RAG (Retrieval-Augmented Generation) operations.
        
        ## Features
        * Document indexing and retrieval
        * Vector similarity search
        * LLM querying with and without RAG
        * Model management
        * Collection management
        
        ## Authentication
        Currently, this API does not require authentication.
        """,
        routes=app.routes,
    )

    # Add tags for better organization
    openapi_schema["tags"] = [
        {
            "name": "Health",
            "description": "Health check and system status endpoints"
        },
        {
            "name": "Collections",
            "description": "Manage vector collections"
        },
        {
            "name": "Models",
            "description": "Manage and interact with LLM models"
        },
        {
            "name": "Documents",
            "description": "Document indexing and management"
        },
        {
            "name": "Search",
            "description": "Search and query operations"
        }
    ]

    app.openapi_schema = openapi_schema
    return app.openapi_schema 