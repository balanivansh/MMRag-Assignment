from pydantic import BaseModel, field_validator
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

    @field_validator("content_types")
    @classmethod
    def validate_content_types(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if v is None:
            return v
        valid_types = {"image", "page_text_plus_ocr", "table", "text"}
        for item in v:
            if item not in valid_types:
                raise ValueError(
                    f"Unsupported content_types: ['{item}']. Valid values are: {sorted(list(valid_types))}"
                )
        return v

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
