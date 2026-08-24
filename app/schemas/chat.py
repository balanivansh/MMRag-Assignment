from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class ChatRequest(BaseModel):
    query: str
    k: Optional[int] = 6
    min_score: Optional[float] = None
    filename: Optional[str] = None
    document_id: Optional[str] = None
    content_types: Optional[List[str]] = None
    page_number: Optional[int] = None
    page_from: Optional[int] = None
    page_to: Optional[int] = None

class SourceMetadata(BaseModel):
    rank: int
    score: float
    filename: str
    page_number: Any
    content_type: str
    citation: str
    document_id: Optional[str] = None
    chunk_id: Optional[str] = None
    chunk_index: Optional[int] = None
    table_index: Optional[Any] = None
    image_index: Optional[Any] = None
    image_path: Optional[str] = None

class UsedImage(BaseModel):
    source_rank: int
    citation: str
    filename: str
    page_number: Any
    image_index: Optional[Any] = None
    image_path: str

class ChatResponse(BaseModel):
    query: str
    answer: str
    sources: List[SourceMetadata]
    used_images: List[UsedImage]
    retrieval_count: int
    model_name: str
    collection_name: str
    usage: Optional[Dict[str, Any]] = None
