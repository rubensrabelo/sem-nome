import os
import json
import aiofiles
from typing import List
from src.config.settings import settings

METADATA_FILE = os.path.join(settings.storage.metadata_dir, "documents.json")

def load_all_metadata() -> List[dict]:
    if not os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)
        return []
    try:
        with open(METADATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def save_all_metadata(data: List[dict]):
    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

async def save_secure_file(file_bytes: bytes, stored_name: str) -> str:
    file_path = os.path.join(settings.storage.documents_dir, stored_name)
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(file_bytes)
    return file_path
