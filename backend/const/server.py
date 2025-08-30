# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware

# from controllers.qdrant_controller import router as vector_database_controller
# from controllers.config_controller import router as config_controller
# from controllers.ollama_controller import router as ollama_controller
# from controllers.files_controller import router as files_controller
# from controllers.chat_controller import router as chat_controller

# app = FastAPI(
#     title="RAG API",
#     description="API for Retrieval-Augmented Generation operations",
#     version="1.0.0",
#     docs_url="/docs",
#     redoc_url="/redoc",
#     openapi_url="/openapi.json",
# )

# app.include_router(vector_database_controller)
# app.include_router(config_controller)
# app.include_router(ollama_controller)
# app.include_router(files_controller)
# app.include_router(chat_controller)

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"], 
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
