import os

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "localhost")
OLLAMA_PORT = os.getenv("OLLAMA_PORT", "11434")
OLLAMA_BASE_URL = f"http://{OLLAMA_HOST}:{OLLAMA_PORT}"
MODEL_NAME_VAL = os.getenv("MODEL_NAME_VAL", "deepseek-r1:8b")

INIT_MODEL_NAME_VAL = os.getenv("INIT_MODEL_NAME_VAL", "SpeakLeash/bielik-7b-instruct-v0.1-gguf:latest")
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-mpnet-base-v2")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/data/uploads")
JOBS_DIR = os.path.join(UPLOAD_DIR, ".jobs")
TMP_DIR = os.path.join(UPLOAD_DIR, "tmp")

QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "rag_collection")
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
QDRANT_URL = os.getenv("QDRANT_URL", f"http://{QDRANT_HOST}:{QDRANT_PORT}")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "rag_collection")
QDRANT_RECREATE_ON_MISMATCH = os.getenv("QDRANT_RECREATE_ON_MISMATCH", "true").lower() == "true"
VECTOR_SIZE = os.getenv('VECTOR_SIZE', 768)