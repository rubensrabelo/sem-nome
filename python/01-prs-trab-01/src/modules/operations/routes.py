import os
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response
from collections import Counter

from src.config.settings import settings
from src.core.logging_config import log_event
from src.modules.vault.service import load_all_metadata
from src.core.security import calculate_sha256
from src.modules.operations.service import generate_csv_report, create_global_zip_backup, create_selective_project_backup

router = APIRouter(prefix="/operations", tags=["System Operations"])

@router.get("/stats")
def get_vault_statistics():
    docs = load_all_metadata()
    total_docs = len(docs)
    total_size = sum([d["size"] for d in docs])
    
    extensions = Counter([d["extension"] for d in docs])
    categories = Counter([d["category"] for d in docs])
    projects = Counter([d["project"] for d in docs])
    
    return {
        "total_documents": total_docs,
        "space_utilized_bytes": total_size,
        "by_extension": dict(extensions),
        "by_category": dict(categories),
        "by_project": dict(projects)
    }

@router.get("/integrity-check")
def global_integrity_check():
    docs = load_all_metadata()
    verified = 0
    intact = 0
    altered = 0
    missing = 0
    
    for d in docs:
        verified += 1
        file_path = os.path.join(settings.storage.documents_dir, d["stored_name"])
        if not os.path.exists(file_path):
            missing += 1
            continue
        with open(file_path, "rb") as f:
            curr_hash = calculate_sha256(f.read())
        if curr_hash == d["sha256"]:
            intact += 1
        else:
            altered += 1
            
    return {
        "documents_verified": verified,
        "documents_intact": intact,
        "documents_altered": altered,
        "missing_physical_files": missing
    }

@router.get("/export/csv")
def export_catalog_as_csv():
    csv_data = generate_csv_report()
    log_event("INFO", "CSV_EXPORT", "Exported catalogue database successfully")
    return Response(
        content=csv_data, 
        media_type="text/csv", 
        headers={"Content-Disposition": "attachment; filename=catalog.csv"}
    )

@router.post("/backup")
def trigger_global_backup():
    filename = create_global_zip_backup()
    log_event("INFO", "GLOBAL_BACKUP", f"Created general backup: {filename}")
    return {"message": "Global backup successfully created", "filename": filename}

@router.post("/backup/project")
def trigger_project_selective_backup(project: str = Query(...)):
    filename = create_selective_project_backup(project)
    if not filename:
        log_event("WARNING", "BACKUP_FAILED", f"No documents found for project: {project}")
        raise HTTPException(status_code=404, detail=f"No documents registered for project '{project}'")
    log_event("INFO", "PROJECT_BACKUP", f"Created selective backup for {project}: {filename}")
    return {"message": "Selective project backup successfully created", "filename": filename}

@router.get("/backups")
def list_available_backups():
    files = os.listdir(settings.storage.backups_dir)
    backup_list = []
    for f in files:
        if f.endswith(".zip"):
            path = os.path.join(settings.storage.backups_dir, f)
            backup_list.append({
                "file": f,
                "size": os.path.getsize(path)
            })
    return backup_list
