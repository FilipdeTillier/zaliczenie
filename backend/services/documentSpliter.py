from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import CharacterTextSplitter
import os
from services.qdrantService import QdrantService
import asyncio
from qdrant_client.models import PointStruct
import numpy as np
from services.openAiService import open_ai_service
import uuid
from fastembed import TextEmbedding
from fastembed.common.model_description import PoolingType, ModelSource

QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "rag_collection")
qdrant_host = os.getenv("QDRANT_HOST", "localhost")
qdrant_port = int(os.getenv("QDRANT_PORT", 6333))

qdrant_client = QdrantService(host=qdrant_host, port=qdrant_port, collection_name=QDRANT_COLLECTION_NAME, vector_size=768)

print('hehehe 2')

TextEmbedding.add_custom_model(
    model="intfloat/multilingual-e5-small",
    pooling=PoolingType.MEAN,
    normalization=True,
    sources=ModelSource(hf="intfloat/multilingual-e5-small"),  # can be used with an `url` to load files from a private storage
    dim=768,
    model_file="onnx/model.onnx",  # can be used to load an already supported model with another optimization or quantization, e.g. onnx/model_O4.onnx
)
model = TextEmbedding(model_name="intfloat/multilingual-e5-small")

async def load_pages():
    pdf_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "polski_lad_3.pdf"))

    loader = PyPDFLoader(pdf_path)
    pages = []
    # documents = [
    # "FastEmbed is lighter than Transformers & Sentence-Transformers.",
    # "FastEmbed is supported by and maintained by Qdrant.",
    # ]

    async for page in loader.alazy_load():        
        # random_id = str(uuid.uuid4())
        pages.append(page)
        # print('=========page_content', page.page_content)


    # embedding_model = TextEmbedding(dim=768)
    # print(embedding_model)
    embeddings_generator = model.embed(pages)
    embeddings_list = list(model.embed(pages))
    print('----------------------', embeddings_generator)
    print('len', len(embeddings_list[0]))
        # qdrant_client.add_document(page.page_content, embedding=embeddings_generator)
    # ===============
    # print('-----pages', pages)
    # embedding_model = TextEmbedding()
    # embeddings_generator = embedding_model.embed(pages)
    # embeddings_list = list(embeddings_generator)
    # len(embeddings_list[0])  
    # print("Embeddings:\n", embeddings_list)
    # =============
    # qdrant_client.add_to_database(pages)
    # embeddings_list = list(embeddings_generator)
    # len(embeddings_list[0])  

asyncio.run(load_pages())

# print(pages)
