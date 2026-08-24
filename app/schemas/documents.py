from pydantic import BaseModel

class UploadResponse(BaseModel):
    collection_name: str
    source_document_count: int
    input_document_count: int
    indexed_document_count: int
    inserted_point_count: int
    pdf_path: str
    parsed_pages: int
    parsed_tables: int
    parsed_images: int
