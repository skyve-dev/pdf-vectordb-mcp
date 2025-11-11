"""
PDF processing module for text extraction and chunking
"""
import logging
from pathlib import Path
from typing import List, Dict, Optional
import pypdf
from .config import Config
from .utils import split_text_with_overlap, create_chunk_id, get_file_hash

logger = logging.getLogger(__name__)

class PDFProcessor:
    """Handles PDF text extraction and chunking"""

    def __init__(self, chunk_size: Optional[int] = None, chunk_overlap: Optional[int] = None):
        """
        Initialize PDF processor

        Args:
            chunk_size: Size of text chunks (defaults to Config.CHUNK_SIZE)
            chunk_overlap: Overlap between chunks (defaults to Config.CHUNK_OVERLAP)
        """
        self.chunk_size = chunk_size or Config.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or Config.CHUNK_OVERLAP

    def extract_text_from_pdf(self, pdf_path: Path) -> List[Dict[str, any]]:
        """
        Extract text from PDF file page by page

        Args:
            pdf_path: Path to the PDF file

        Returns:
            List of dictionaries containing page text and metadata

        Raises:
            Exception: If PDF cannot be read
        """
        try:
            pages_data = []
            with open(pdf_path, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                num_pages = len(pdf_reader.pages)

                logger.info(f"Processing {pdf_path.name}: {num_pages} pages")

                for page_num, page in enumerate(pdf_reader.pages, start=1):
                    text = page.extract_text()

                    # Clean up the text
                    text = self._clean_text(text)

                    if text.strip():  # Only include pages with actual content
                        pages_data.append({
                            'page_number': page_num,
                            'text': text,
                            'document': pdf_path.name
                        })

            logger.info(f"Extracted text from {len(pages_data)} pages in {pdf_path.name}")
            return pages_data

        except Exception as e:
            logger.error(f"Error extracting text from {pdf_path}: {e}")
            raise

    def _clean_text(self, text: str) -> str:
        """
        Clean extracted text

        Args:
            text: Raw extracted text

        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = ' '.join(text.split())

        # Remove common PDF artifacts
        text = text.replace('\x00', '')

        return text

    def chunk_pages(self, pages_data: List[Dict[str, any]]) -> List[Dict[str, any]]:
        """
        Split pages into chunks with metadata

        Args:
            pages_data: List of page dictionaries from extract_text_from_pdf

        Returns:
            List of chunk dictionaries with text and metadata
        """
        chunks = []

        for page_data in pages_data:
            page_text = page_data['text']
            page_num = page_data['page_number']
            doc_name = page_data['document']

            # Split page text into chunks
            text_chunks = split_text_with_overlap(
                page_text,
                self.chunk_size,
                self.chunk_overlap
            )

            # Create chunk metadata
            for chunk_idx, chunk_text in enumerate(text_chunks):
                chunk_id = create_chunk_id(doc_name, page_num, chunk_idx)

                chunks.append({
                    'id': chunk_id,
                    'text': chunk_text,
                    'metadata': {
                        'document': doc_name,
                        'page': page_num,
                        'chunk_index': chunk_idx,
                        'total_chunks_on_page': len(text_chunks)
                    }
                })

        logger.info(f"Created {len(chunks)} chunks from {len(pages_data)} pages")
        return chunks

    def process_pdf(self, pdf_path: Path) -> Dict[str, any]:
        """
        Complete processing pipeline for a PDF file

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Dictionary containing chunks and document metadata
        """
        try:
            # Extract text from pages
            pages_data = self.extract_text_from_pdf(pdf_path)

            # Chunk the pages
            chunks = self.chunk_pages(pages_data)

            # Calculate file hash for change detection
            file_hash = get_file_hash(pdf_path)

            return {
                'document': pdf_path.name,
                'file_hash': file_hash,
                'num_pages': len(pages_data),
                'num_chunks': len(chunks),
                'chunks': chunks
            }

        except Exception as e:
            logger.error(f"Error processing PDF {pdf_path}: {e}")
            raise

    def process_all_pdfs(self, pdf_folder: Path) -> List[Dict[str, any]]:
        """
        Process all PDF files in a folder

        Args:
            pdf_folder: Path to folder containing PDFs

        Returns:
            List of processed document dictionaries
        """
        pdf_files = list(pdf_folder.glob("*.pdf"))
        logger.info(f"Found {len(pdf_files)} PDF files in {pdf_folder}")

        processed_docs = []
        for pdf_path in pdf_files:
            try:
                result = self.process_pdf(pdf_path)
                processed_docs.append(result)
            except Exception as e:
                logger.warning(f"Skipping {pdf_path.name} due to error: {e}")
                continue

        logger.info(f"Successfully processed {len(processed_docs)} documents")
        return processed_docs
