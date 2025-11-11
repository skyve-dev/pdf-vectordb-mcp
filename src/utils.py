"""
Utility functions and helpers
"""
import logging
import hashlib
from pathlib import Path
from typing import List
from .config import Config

def setup_logging():
    """Set up logging configuration"""
    logging.basicConfig(
        level=getattr(logging, Config.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('pdf_vectordb_mcp.log')
        ]
    )
    return logging.getLogger(__name__)

def get_file_hash(file_path: Path) -> str:
    """
    Calculate MD5 hash of a file for change detection

    Args:
        file_path: Path to the file

    Returns:
        MD5 hash as hex string
    """
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def create_chunk_id(doc_name: str, page_num: int, chunk_idx: int) -> str:
    """
    Create a unique identifier for a chunk

    Args:
        doc_name: Document filename
        page_num: Page number
        chunk_idx: Chunk index on the page

    Returns:
        Unique chunk ID
    """
    return f"{doc_name}::page_{page_num}::chunk_{chunk_idx}"

def split_text_with_overlap(text: str, chunk_size: int, overlap: int) -> List[str]:
    """
    Split text into chunks with overlap

    Args:
        text: Text to split
        chunk_size: Target size of each chunk in characters
        overlap: Number of overlapping characters between chunks

    Returns:
        List of text chunks
    """
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size

        # If not the last chunk, try to break at a sentence or word boundary
        if end < len(text):
            # Look for sentence boundary (. ! ?) within the last 20% of chunk
            search_start = int(end - chunk_size * 0.2)
            sentence_breaks = [text.rfind('. ', search_start, end),
                             text.rfind('! ', search_start, end),
                             text.rfind('? ', search_start, end)]
            best_break = max(sentence_breaks)

            if best_break > start:
                end = best_break + 1
            else:
                # Fall back to word boundary
                space_pos = text.rfind(' ', start, end)
                if space_pos > start:
                    end = space_pos

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        # Move start position, accounting for overlap
        start = end - overlap if end < len(text) else end

    return chunks

def format_source_citation(metadata: dict) -> str:
    """
    Format metadata into a readable source citation

    Args:
        metadata: Dictionary containing document metadata

    Returns:
        Formatted citation string
    """
    doc_name = metadata.get('document', 'Unknown')
    page = metadata.get('page', 'Unknown')
    return f"{doc_name} (Page {page})"

logger = setup_logging()
