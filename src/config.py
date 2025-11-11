"""
Configuration management for PDF Vector DB MCP Server
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the application"""

    # Embedding Configuration (local sentence-transformers)
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-mpnet-base-v2")
    EMBEDDING_DEVICE = os.getenv("EMBEDDING_DEVICE", "auto")  # "cpu", "cuda", or "auto"

    # Paths
    BASE_DIR = Path(__file__).parent.parent
    PDF_FOLDER = Path(os.getenv("PDF_FOLDER", BASE_DIR / "data" / "pdfs"))
    CHROMA_DB_PATH = Path(os.getenv("CHROMA_DB_PATH", BASE_DIR / "data" / "chroma_db"))

    # Chunking Configuration
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "800"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))

    # Retrieval Configuration
    DEFAULT_TOP_K = int(os.getenv("DEFAULT_TOP_K", "5"))

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    # Collection name for ChromaDB
    COLLECTION_NAME = "pdf_documents"

    @classmethod
    def validate(cls):
        """Validate that all required configuration is present"""
        # Ensure directories exist
        cls.PDF_FOLDER.mkdir(parents=True, exist_ok=True)
        cls.CHROMA_DB_PATH.mkdir(parents=True, exist_ok=True)

        return True

    @classmethod
    def get_summary(cls):
        """Get a summary of current configuration"""
        return {
            "embedding_model": cls.EMBEDDING_MODEL,
            "embedding_device": cls.EMBEDDING_DEVICE,
            "pdf_folder": str(cls.PDF_FOLDER),
            "chroma_db_path": str(cls.CHROMA_DB_PATH),
            "chunk_size": cls.CHUNK_SIZE,
            "chunk_overlap": cls.CHUNK_OVERLAP,
            "default_top_k": cls.DEFAULT_TOP_K,
            "log_level": cls.LOG_LEVEL,
        }
