from fastapi import Request

def get_ingestion_service(request: Request):
    return request.app.state.ingestion_service

def get_retrieval_service(request: Request):
    return request.app.state.retrieval_service

def get_generation_service(request: Request):
    return request.app.state.generation_service
