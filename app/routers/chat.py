from fastapi import APIRouter, Depends
from app.dependencies import get_generation_service
from app.schemas.chat import ChatRequest, ChatResponse
from src.generation import MultimodalRAGGenerator

router = APIRouter()

@router.post("", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    generation_service: MultimodalRAGGenerator = Depends(get_generation_service)
):
    result = generation_service.generate(
        query=request.query,
        k=request.k,
        min_score=request.min_score,
        filename=request.filename,
        document_id=request.document_id,
        content_types=request.content_types,
        page_number=request.page_number,
        page_from=request.page_from,
        page_to=request.page_to,
    )
    return result
