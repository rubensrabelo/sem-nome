from fastapi import FastAPI
from .core.logging_config import setup_logging, log_event
from .modules.vault.routes import router as vault_router
from .modules.operations.routes import router as operations_router

app = FastAPI(
    title="Science Research Artifacts Vault API",
    description="Modular monolith digital secure repository tailored for scientific research preservation.",
    version="1.0.0"
)

setup_logging()
log_event("INFO", "SYSTEM_START", "Vault application ecosystem successfully initialized.")

app.include_router(vault_router)
app.include_router(operations_router)

@app.get("/")
def root():
    return {
        "status": "online",
        "system": "Science Research Artifacts Vault",
        "documentation_url": "/docs"
    }
