from fastapi import APIRouter, Depends
from app.dependencies import get_retrieval_service
from src.retriever import MultimodalQdrantRetriever

router = APIRouter()

@router.get("")
def health_check(
    retrieval_service: MultimodalQdrantRetriever = Depends(get_retrieval_service)
):
    status = retrieval_service.collection_status()
    return {"status": "ok", "collection": status}
