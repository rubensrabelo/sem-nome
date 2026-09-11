import os
import yaml
from pydantic import BaseModel
from pydantic_settings import BaseSettings

class StorageConfig(BaseModel):
    documents_dir: str
    metadata_dir: str
    backups_dir: str
    logs_dir: str

class UploadConfig(BaseModel):
    max_size_mb: int

class HashConfig(BaseModel):
    algorithm: str

class LoggingConfig(BaseModel):
    file_path: str
    level: str

class BackupConfig(BaseModel):
    format: str

class Settings(BaseSettings):
    storage: StorageConfig
    upload: UploadConfig
    hash: HashConfig
    logging: LoggingConfig
    backup: BackupConfig

    @classmethod
    def load_settings(cls, yaml_path: str = "config.yaml") -> "Settings":
        if not os.path.exists(yaml_path):
            raise FileNotFoundError(f"Configuration file {yaml_path} not found.")
        with open(yaml_path, "r", encoding="utf-8") as f:
            config_data = yaml.safe_load(f)
        return cls(**config_data)

settings = Settings.load_settings()

for attr, path in settings.storage.model_dump().items():
    os.makedirs(path, exist_ok=True)
