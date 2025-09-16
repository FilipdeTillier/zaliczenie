import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, UnstructuredWordDocumentLoader, UnstructuredPowerPointLoader
from typing import List, Dict, Any, Tuple

def get_text_splitter(chunk_size: int = 1000, overlap: int = 200) -> RecursiveCharacterTextSplitter:
    return RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=overlap)

def chunk_file(abs_path: str, chunk_size: int = 1000, overlap: int = 200) -> List[Dict[str, Any]]:
    """
    Chunk a file and return chunks with metadata including page numbers.
    
    Returns:
        List of dictionaries containing 'text' and 'metadata' keys
    """
    extension = os.path.splitext(abs_path)[1].lower()
    splitter = get_text_splitter(chunk_size, overlap)
    
    if extension == ".pdf":
        loader = PyPDFLoader(abs_path)
        docs = loader.load()
        parts = splitter.split_documents(docs)
        chunks = []
        for part in parts:
            # Extract page number from metadata if available
            page_number = part.metadata.get('page', None)
            if page_number is not None:
                page_number = int(page_number) + 1  # Convert to 1-based indexing
            else:
                page_number = None
                
            chunks.append({
                "text": part.page_content,
                "metadata": {
                    "page_number": page_number,
                    "source_type": "pdf",
                    "chunk_size": len(part.page_content)
                }
            })
        return chunks
        
    elif extension in {".docx", ".doc"}:
        try:
            loader = UnstructuredWordDocumentLoader(abs_path)
            docs = loader.load()
            parts = splitter.split_documents(docs)
            chunks = []
            for part in parts:
                # Word documents typically don't have page numbers in metadata
                chunks.append({
                    "text": part.page_content,
                    "metadata": {
                        "page_number": None,
                        "source_type": "word",
                        "chunk_size": len(part.page_content)
                    }
                })
            return chunks
        except Exception:
            # Fallback to text extraction if Word loader fails
            return chunk_file_as_text(abs_path, splitter, "word")
            
    elif extension in {".pptx", ".ppt"}:
        try:
            loader = UnstructuredPowerPointLoader(abs_path)
            docs = loader.load()
            parts = splitter.split_documents(docs)
            chunks = []
            for part in parts:
                # PowerPoint slides might have slide numbers
                slide_number = part.metadata.get('slide_number', None)
                chunks.append({
                    "text": part.page_content,
                    "metadata": {
                        "page_number": slide_number,
                        "source_type": "powerpoint",
                        "chunk_size": len(part.page_content)
                    }
                })
            return chunks
        except Exception:
            # Fallback to text extraction if PowerPoint loader fails
            return chunk_file_as_text(abs_path, splitter, "powerpoint")
            
    elif extension in {".txt", ".md", ".rtf", ".csv"}:
        return chunk_file_as_text(abs_path, splitter, extension[1:])
    
    return []

def chunk_file_as_text(abs_path: str, splitter: RecursiveCharacterTextSplitter, source_type: str) -> List[Dict[str, Any]]:
    """Fallback method for text-based files that don't have page information."""
    try:
        with open(abs_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
        parts = splitter.split_text(text)
        chunks = []
        for part in parts:
            chunks.append({
                "text": part,
                "metadata": {
                    "page_number": None,
                    "source_type": source_type,
                    "chunk_size": len(part)
                }
            })
        return chunks
    except Exception:
        return []
