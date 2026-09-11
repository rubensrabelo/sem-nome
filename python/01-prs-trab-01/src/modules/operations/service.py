import os
import csv
import zipfile
from io import StringIO
from datetime import datetime
from src.config.settings import settings
from src.modules.vault.service import load_all_metadata

def generate_csv_report() -> str:
    docs = load_all_metadata()
    output = StringIO()
    writer = csv.writer(output)
    
    writer.writerow([
        "id", "original_name", "extension", "category", "size", 
        "upload_date", "sha256", "project", "researcher", "artifact_type"
    ])
    
    for d in docs:
        writer.writerow([
            d["id"], d["original_name"], d["extension"], d["category"], d["size"], 
            d["upload_date"], d["sha256"], d["project"], d["researcher"], d["artifact_type"]
        ])
    return output.getvalue()

def create_global_zip_backup() -> str:
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    backup_filename = f"backup_{timestamp}.zip"
    backup_path = os.path.join(settings.storage.backups_dir, backup_filename)
    
    docs = load_all_metadata()
    with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for d in docs:
            file_path = os.path.join(settings.storage.documents_dir, d["stored_name"])
            if os.path.exists(file_path):
                zipf.write(file_path, arcname=d["stored_name"])
    return backup_filename

def create_selective_project_backup(project_name: str) -> str:
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    safe_project_name = "".join([c for c in project_name if c.isalnum() or c in (' ', '_', '-')]).rstrip()
    backup_filename = f"backup_project_{safe_project_name.replace(' ', '_')}_{timestamp}.zip"
    backup_path = os.path.join(settings.storage.backups_dir, backup_filename)
    
    docs = load_all_metadata()
    filtered_docs = [d for d in docs if d["project"].lower() == project_name.lower()]
    
    if not filtered_docs:
        return ""
        
    with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for d in filtered_docs:
            file_path = os.path.join(settings.storage.documents_dir, d["stored_name"])
            if os.path.exists(file_path):
                zipf.write(file_path, arcname=d["stored_name"])
    return backup_filename
