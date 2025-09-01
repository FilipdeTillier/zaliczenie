from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class Document(BaseModel):
    filename: str
    checksum_sha256: str
    size_bytes: int
    storage_key: str
    content_type: str
    created_at: str
    download_url: str

class OpenAIMessage(BaseModel):
    role: str
    content: str

class OpenAIChatRequest(BaseModel):
    model: str
    messages: List[OpenAIMessage]
    documents: Optional[List[Document]] = Field(default_factory=list, description="List of documents to search in Qdrant")
    max_results: Optional[int] = Field(default=5, ge=1, le=20, description="Maximum number of results to return from Qdrant search")

class OpenAIContentItem(BaseModel):
    type: str
    annotations: Optional[List[Any]] = None
    logprobs: Optional[List[Any]] = None
    text: Optional[str] = None

class OpenAIOutputMessage(BaseModel):
    id: str
    type: str
    status: str
    content: List[OpenAIContentItem]
    role: str

class OpenAIReasoning(BaseModel):
    effort: Optional[Any] = None
    summary: Optional[Any] = None

class OpenAITextFormat(BaseModel):
    type: str

class OpenAIText(BaseModel):
    format: OpenAITextFormat

class OpenAIUsageDetails(BaseModel):
    cached_tokens: Optional[int] = None

class OpenAIOutputTokensDetails(BaseModel):
    reasoning_tokens: Optional[int] = None

class OpenAIUsage(BaseModel):
    input_tokens: int
    input_tokens_details: Optional[OpenAIUsageDetails] = None
    output_tokens: int
    output_tokens_details: Optional[OpenAIOutputTokensDetails] = None
    total_tokens: int

class OpenAIResponse(BaseModel):
    id: str
    object: str
    created_at: int
    status: str
    background: Optional[bool] = None
    error: Optional[Any] = None
    incomplete_details: Optional[Any] = None
    instructions: Optional[Any] = None
    max_output_tokens: Optional[Any] = None
    max_tool_calls: Optional[Any] = None
    model: str
    output: List[OpenAIOutputMessage]
    parallel_tool_calls: Optional[bool] = None
    previous_response_id: Optional[str] = None
    reasoning: Optional[OpenAIReasoning] = None
    service_tier: Optional[str] = None
    store: Optional[bool] = None
    temperature: Optional[float] = None
    text: Optional[OpenAIText] = None
    tool_choice: Optional[str] = None
    tools: Optional[List[Any]] = None
    top_logprobs: Optional[int] = None
    top_p: Optional[float] = None
    truncation: Optional[str] = None
    usage: Optional[OpenAIUsage] = None
    user: Optional[Any] = None
    metadata: Optional[Dict[str, Any]] = None
