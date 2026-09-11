from pydantic import BaseModel, Field
from typing import Optional

class DocumentMetadata(BaseModel):
    id: int
    original_name: str
    stored_name: str
    extension: str
    mime_type: str
    size: int
    category: str
    description: str
    upload_date: str
    sha256: str
    project: str
    researcher: str
    artifact_type: str
    research_stage: str
    reference_date: str

class DocumentUpdate(BaseModel):
    category: Optional[str] = None
    description: Optional[str] = None
    project: Optional[str] = None
    researcher: Optional[str] = None
    artifact_type: Optional[str] = None
    research_stage: Optional[str] = None
