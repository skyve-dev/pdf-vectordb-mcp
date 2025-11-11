"""
Tests for utility functions
"""
import pytest
from src.utils import (
    split_text_with_overlap,
    create_chunk_id,
    format_source_citation
)

def test_split_text_with_overlap():
    """Test text chunking with overlap"""
    text = "This is a test. " * 100  # Create a long text
    chunks = split_text_with_overlap(text, chunk_size=100, overlap=20)

    assert len(chunks) > 0
    # Each chunk should be roughly the target size
    for chunk in chunks:
        assert len(chunk) <= 150  # Allow some flexibility

def test_split_text_short():
    """Test that short text returns single chunk"""
    text = "Short text"
    chunks = split_text_with_overlap(text, chunk_size=100, overlap=20)

    assert len(chunks) == 1
    assert chunks[0] == text

def test_create_chunk_id():
    """Test chunk ID creation"""
    chunk_id = create_chunk_id("document.pdf", 5, 2)

    assert "document.pdf" in chunk_id
    assert "page_5" in chunk_id
    assert "chunk_2" in chunk_id

def test_format_source_citation():
    """Test source citation formatting"""
    metadata = {
        'document': 'test.pdf',
        'page': 10
    }

    citation = format_source_citation(metadata)

    assert "test.pdf" in citation
    assert "10" in citation

def test_format_source_citation_missing_data():
    """Test citation with missing metadata"""
    metadata = {}

    citation = format_source_citation(metadata)

    assert "Unknown" in citation
