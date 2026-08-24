import os
from functools import lru_cache
from typing import Optional
from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    google_api_key: Optional[str] = Field(None, validation_alias="GOOGLE_API_KEY")
    gemini_api_key: Optional[str] = Field(None, validation_alias="GEMINI_API_KEY")
    groq_api_key: Optional[str] = Field(None, validation_alias="GROQ_API_KEY")
    
    qdrant_url: Optional[str] = Field(None, validation_alias="QDRANT_URL")
    qdrant_cluster_endpoint: Optional[str] = Field(None, validation_alias="QDRANT_Cluster_Endpoint")
    qdrant_api_key: Optional[str] = Field(None, validation_alias="QDRANT_API_KEY")
    qdrant_collection_name: str = Field("mm-rag-documents", validation_alias="QDRANT_COLLECTION_NAME")
    
    gemini_embedding_model: str = Field("models/gemini-embedding-2", validation_alias="GEMINI_EMBEDDING_MODEL")
    gemini_embedding_dimension: int = Field(3072, validation_alias="GEMINI_EMBEDDING_DIMENSION")
    
    groq_chat_model: str = Field("qwen/qwen3.6-27b", validation_alias="GROQ_CHAT_MODEL")
    tesseract_path: Optional[str] = Field(None, validation_alias="TESSERACT_PATH")
    
    upload_dir: str = Field("./data/uploads", validation_alias="UPLOAD_DIR")
    parsed_output_dir: str = Field("./data/parsed_pdf_output", validation_alias="PARSED_OUTPUT_DIR")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    @model_validator(mode="after")
    def validate_required_settings(self) -> "Settings":
        # Check Gemini / Google API Key
        if not self.google_api_key and not self.gemini_api_key:
            raise ValueError("GOOGLE_API_KEY or GEMINI_API_KEY is missing")
        # Check Groq API Key
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY is missing")
        # Check Qdrant connection endpoint
        if not self.qdrant_url and not self.qdrant_cluster_endpoint:
            raise ValueError("QDRANT_URL is missing")
        return self

    @property
    def final_gemini_api_key(self) -> str:
        return self.gemini_api_key or self.google_api_key or ""

    @property
    def final_qdrant_url(self) -> str:
        return self.qdrant_url or self.qdrant_cluster_endpoint or ""

@lru_cache()
def get_settings() -> Settings:
    return Settings()
