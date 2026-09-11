import os
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Query
from fastapi.responses import FileResponse
from typing import List, Optional

from src.config.settings import settings
from src.core.logging_config import log_event
from src.core.security import calculate_sha256
from src.modules.vault.models import DocumentMetadata, DocumentUpdate
from src.modules.vault.service import load_all_metadata, save_all_metadata, save_secure_file

router = APIRouter(prefix="/documents", tags=["Documents Vault"])

@router.post("", response_model=DocumentMetadata, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    category: str = Form(...),
    description: str = Form(...),
    project: str = Form(...),
    researcher: str = Form(...),
    artifact_type: str = Form(...),
    research_stage: str = Form(...),
    reference_date: str = Form(...)
):
    content = await file.read()
    size = len(content)
    
    if size > settings.upload.max_size_mb * 1024 * 1024:
        log_event("ERROR", "UPLOAD_FAILED", "File exceeds size limit")
        raise HTTPException(status_code=400, detail="File size exceeds limit.")

    metadata_list = load_all_metadata()
    next_id = max([doc["id"] for doc in metadata_list], default=0) + 1
    
    _, ext = os.path.splitext(file.filename)
    stored_name = f"{next_id}_{file.filename}"
    sha256_value = calculate_sha256(content)

    await save_secure_file(content, stored_name)

    new_doc = DocumentMetadata(
        id=next_id,
        original_name=file.filename,
        stored_name=stored_name,
        extension=ext,
        mime_type=file.content_type or "application/octet-stream",
        size=size,
        category=category,
        description=description,
        upload_date=datetime.now().isoformat(),
        sha256=sha256_value,
        project=project,
        researcher=researcher,
        artifact_type=artifact_type,
        research_stage=research_stage,
        reference_date=reference_date
    )

    metadata_list.append(new_doc.model_dump())
    save_all_metadata(metadata_list)
    
    log_event("INFO", "UPLOAD", f"id={next_id} file={file.filename}")
    return new_doc

@router.get("", response_model=List[DocumentMetadata])
def list_documents(
    project: Optional[str] = Query(None),
    researcher: Optional[str] = Query(None),
    category: Optional[str] = Query(None)
):
    docs = load_all_metadata()
    if project:
        docs = [d for d in docs if project.lower() in d["project"].lower()]
    if researcher:
        docs = [d for d in docs if researcher.lower() in d["researcher"].lower()]
    if category:
        docs = [d for d in docs if category.lower() == d["category"].lower()]
    return docs

@router.get("/{id}", response_model=DocumentMetadata)
def get_document_details(id: int):
    docs = load_all_metadata()
    for doc in docs:
        if doc["id"] == id:
            return doc
    log_event("ERROR", "DOCUMENT_NOT_FOUND", f"id={id}")
    raise HTTPException(status_code=404, detail="Document not found")

@router.get("/{id}/download")
def download_document(id: int):
    docs = load_all_metadata()
    for doc in docs:
        if doc["id"] == id:
            file_path = os.path.join(settings.storage.documents_dir, doc["stored_name"])
            if not os.path.exists(file_path):
                log_event("ERROR", "FILE_PHYSICALLY_MISSING", f"id={id}")
                raise HTTPException(status_code=404, detail="Physical file missing from storage")
            log_event("INFO", "DOWNLOAD", f"id={id} file={doc['original_name']}")
            return FileResponse(file_path, media_type=doc["mime_type"], filename=doc["original_name"])
    raise HTTPException(status_code=404, detail="Document metadata not found")

@router.put("/{id}", response_model=DocumentMetadata)
def update_document_metadata(id: int, payload: DocumentUpdate):
    docs = load_all_metadata()
    for doc in docs:
        if doc["id"] == id:
            update_data = payload.model_dump(exclude_unset=True)
            doc.update(update_data)
            save_all_metadata(docs)
            log_event("INFO", "UPDATE", f"id={id}")
            return doc
    raise HTTPException(status_code=404, detail="Document not found")

@router.delete("/{id}", status_code=200)
def delete_document(id: int):
    docs = load_all_metadata()
    for idx, doc in enumerate(docs):
        if doc["id"] == id:
            file_path = os.path.join(settings.storage.documents_dir, doc["stored_name"])
            if os.path.exists(file_path):
                os.remove(file_path)
            docs.pop(idx)
            save_all_metadata(docs)
            log_event("INFO", "DELETE", f"id={id}")
            return {"detail": "Document successfully deleted"}
    raise HTTPException(status_code=404, detail="Document not found")

@router.get("/{id}/integrity")
def check_document_integrity(id: int):
    docs = load_all_metadata()
    for doc in docs:
        if doc["id"] == id:
            file_path = os.path.join(settings.storage.documents_dir, doc["stored_name"])
            if not os.path.exists(file_path):
                log_event("WARNING", "INTEGRITY_FAILED", f"id={id} status=missing")
                return {"id": id, "name": doc["original_name"], "intact": False, "status": "Physical file missing"}
            
            with open(file_path, "rb") as f:
                current_hash = calculate_sha256(f.read())
            
            is_intact = current_hash == doc["sha256"]
            if not is_intact:
                log_event("WARNING", "INTEGRITY_FAILED", f"id={id} status=altered")
            else:
                log_event("INFO", "INTEGRITY_CHECK", f"id={id} intact=True")
                
            return {
                "id": id,
                "name": doc["original_name"],
                "hash_original": doc["sha256"],
                "hash_current": current_hash,
                "intact": is_intact
            }
    raise HTTPException(status_code=404, detail="Document not found")
