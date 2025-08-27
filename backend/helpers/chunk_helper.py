import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from typing import List

def get_text_splitter(chunk_size: int = 1000, overlap: int = 200) -> RecursiveCharacterTextSplitter:
    return RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=overlap)

def chunk_file(abs_path: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    extension = os.path.splitext(abs_path)[1].lower()

    splitter = get_text_splitter(chunk_size, overlap)
    
    if extension == ".pdf":
        loader = PyPDFLoader(abs_path)
        docs = loader.load()
        parts = splitter.split_documents(docs)
        return [d.page_content for d in parts]
    if extension in {".txt", ".md"}:
        with open(abs_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
        return splitter.split_text(text)
    return []
