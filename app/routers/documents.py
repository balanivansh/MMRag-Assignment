from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from pathlib import Path
from app.dependencies import get_ingestion_service
from app.config import get_settings, Settings
from app.schemas.documents import UploadResponse
from src.ingestion import MultimodalDocumentIngestion

router = APIRouter()

@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    settings: Settings = Depends(get_settings),
    ingestion_service: MultimodalDocumentIngestion = Depends(get_ingestion_service)
):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = upload_dir / file.filename
    
    # Save the file locally using its original name
    contents = await file.read()
    with open(file_path, "wb") as f:
        f.write(contents)
        
    # Run parsing and ingestion synchronously
    result = ingestion_service.ingest_pdf(
        pdf_path=str(file_path),
        output_dir=settings.parsed_output_dir,
        tesseract_path=settings.tesseract_path,
        replace_existing=True
    )
    
    return result
