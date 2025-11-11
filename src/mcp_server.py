"""
MCP Server implementation for PDF Vector DB RAG System (using FastMCP)
"""
import asyncio
import logging
from pathlib import Path
from typing import Optional
from fastmcp import FastMCP
from .config import Config
from .pdf_processor import PDFProcessor
from .embeddings import EmbeddingGenerator
from .vector_store import VectorStore
from .file_watcher import PDFWatcher
from .utils import format_source_citation

logger = logging.getLogger(__name__)

# Initialize FastMCP
mcp = FastMCP("PDF Vector DB")

# Global components (initialized on startup)
pdf_processor = None
embedding_generator = None
vector_store = None
file_watcher = None


async def process_pdf_file(pdf_path: Path):
    """
    Process a single PDF file

    Args:
        pdf_path: Path to the PDF file
    """
    try:
        logger.info(f"Processing PDF: {pdf_path.name}")

        # Process PDF
        result = pdf_processor.process_pdf(pdf_path)

        # Generate embeddings
        chunks_with_embeddings = embedding_generator.embed_chunks(result['chunks'])

        # Extract embeddings
        embeddings = [chunk['embedding'] for chunk in chunks_with_embeddings]

        # Store in vector database
        vector_store.add_chunks(result['chunks'], embeddings)

        logger.info(f"Successfully indexed {result['num_chunks']} chunks from {pdf_path.name}")

    except Exception as e:
        logger.error(f"Error processing PDF {pdf_path}: {e}")
        raise


async def handle_modified(pdf_path: Path):
    """Handle modified PDF file"""
    try:
        # Delete old version
        vector_store.delete_by_document(pdf_path.name)

        # Re-index
        await process_pdf_file(pdf_path)

    except Exception as e:
        logger.error(f"Error handling modified file {pdf_path}: {e}")


def handle_deleted(pdf_path: Path):
    """Handle deleted PDF file"""
    try:
        vector_store.delete_by_document(pdf_path.name)
        logger.info(f"Removed {pdf_path.name} from index")

    except Exception as e:
        logger.error(f"Error handling deleted file {pdf_path}: {e}")


async def index_existing_pdfs():
    """Index all existing PDFs in the folder"""
    try:
        pdf_files = list(Config.PDF_FOLDER.glob("*.pdf"))

        if not pdf_files:
            logger.info("No existing PDFs found to index")
            return

        logger.info(f"Indexing {len(pdf_files)} existing PDFs...")

        for pdf_path in pdf_files:
            # Check if already indexed
            doc_info = vector_store.get_document_info(pdf_path.name)
            if doc_info:
                logger.info(f"Skipping {pdf_path.name} (already indexed)")
                continue

            await process_pdf_file(pdf_path)

        logger.info("Finished indexing existing PDFs")

    except Exception as e:
        logger.error(f"Error indexing existing PDFs: {e}")
        raise


@mcp.resource("config://system")
def get_config() -> str:
    """Get current system configuration"""
    config = Config.get_summary()
    return str(config)


@mcp.tool()
def query_documents(query: str, top_k: int = Config.DEFAULT_TOP_K, document: Optional[str] = None) -> str:
    """
    Search through indexed PDF documents using natural language queries.
    Returns relevant chunks with source citations.

    Args:
        query: Natural language query to search for in the documents
        top_k: Number of results to return (default: 5)
        document: Optional: Filter results to a specific document name

    Returns:
        Search results with source citations and relevance scores
    """
    try:
        # Generate query embedding
        query_embedding = embedding_generator.generate_embedding(query)

        # Build filter if document specified
        filter_dict = {"document": document} if document else None

        # Query vector store
        results = vector_store.query(
            query_embedding=query_embedding,
            top_k=top_k,
            filter_dict=filter_dict
        )

        # Format results
        if not results['ids'][0]:
            return "No relevant documents found for your query."

        response_parts = [f"Found {len(results['ids'][0])} relevant chunks:\n"]

        for i, (doc_id, document_text, metadata, distance) in enumerate(
            zip(results['ids'][0], results['documents'][0],
                results['metadatas'][0], results['distances'][0]), 1
        ):
            similarity_score = 1 - distance  # Convert distance to similarity
            source = format_source_citation(metadata)

            response_parts.append(f"\n--- Result {i} ---")
            response_parts.append(f"Source: {source}")
            response_parts.append(f"Relevance: {similarity_score:.2%}")
            response_parts.append(f"\n{document_text}\n")

        return "\n".join(response_parts)

    except Exception as e:
        logger.error(f"Error in query_documents: {e}")
        return f"Error: {str(e)}"


@mcp.tool()
def list_documents() -> str:
    """
    List all indexed PDF documents with statistics (number of chunks and pages).

    Returns:
        List of indexed documents with their statistics
    """
    try:
        documents = vector_store.list_documents()

        if not documents:
            return "No documents are currently indexed."

        response_parts = [f"Indexed Documents ({len(documents)}):\n"]

        for doc in documents:
            response_parts.append(
                f"- {doc['document']}: {doc['num_pages']} pages, "
                f"{doc['num_chunks']} chunks"
            )

        return "\n".join(response_parts)

    except Exception as e:
        logger.error(f"Error in list_documents: {e}")
        return f"Error: {str(e)}"


@mcp.tool()
def get_document_info(document: str) -> str:
    """
    Get detailed information about a specific indexed document.

    Args:
        document: Name of the document to get information about

    Returns:
        Detailed information about the document
    """
    try:
        info = vector_store.get_document_info(document)

        if not info:
            return f"Document '{document}' not found in the index."

        response = (
            f"Document: {info['document']}\n"
            f"Pages: {info['num_pages']}\n"
            f"Chunks: {info['num_chunks']}\n"
            f"Page numbers: {', '.join(map(str, info['pages']))}"
        )

        return response

    except Exception as e:
        logger.error(f"Error in get_document_info: {e}")
        return f"Error: {str(e)}"


@mcp.tool()
async def reindex_document(document: str) -> str:
    """
    Manually trigger re-indexing of a specific PDF document.

    Args:
        document: Name of the PDF document to re-index

    Returns:
        Status message about the re-indexing operation
    """
    try:
        pdf_path = Config.PDF_FOLDER / document

        if not pdf_path.exists():
            return f"PDF file '{document}' not found in {Config.PDF_FOLDER}"

        # Delete existing chunks
        vector_store.delete_by_document(document)

        # Process the PDF
        await process_pdf_file(pdf_path)

        return f"Successfully re-indexed '{document}'"

    except Exception as e:
        logger.error(f"Error in reindex_document: {e}")
        return f"Error: {str(e)}"


@mcp.tool()
def get_system_stats() -> str:
    """
    Get statistics about the RAG system (total documents, chunks, configuration).

    Returns:
        System statistics and configuration information
    """
    try:
        stats = vector_store.get_stats()
        config = Config.get_summary()

        response = (
            "=== System Statistics ===\n\n"
            f"Total Documents: {stats['total_documents']}\n"
            f"Total Chunks: {stats['total_chunks']}\n\n"
            "=== Configuration ===\n\n"
            f"Embedding Model: {config['embedding_model']}\n"
            f"Embedding Device: {config.get('embedding_device', 'auto')}\n"
            f"PDF Folder: {config['pdf_folder']}\n"
            f"Chunk Size: {config['chunk_size']}\n"
            f"Chunk Overlap: {config['chunk_overlap']}\n"
            f"Default Top-K: {config['default_top_k']}\n\n"
            f"File Watcher: {'Active' if file_watcher and file_watcher.is_running() else 'Inactive'}"
        )

        return response

    except Exception as e:
        logger.error(f"Error in get_system_stats: {e}")
        return f"Error: {str(e)}"


def initialize():
    """Initialize all components on server startup"""
    global pdf_processor, embedding_generator, vector_store, file_watcher

    try:
        logger.info("Initializing PDF Vector DB MCP Server...")

        # Validate configuration
        Config.validate()

        # Initialize components
        pdf_processor = PDFProcessor()
        embedding_generator = EmbeddingGenerator()
        vector_store = VectorStore()

        # Validate embedding model
        if not embedding_generator.validate_connection():
            raise Exception("Failed to load embedding model")

        logger.info("PDF Vector DB MCP Server components initialized")

    except Exception as e:
        logger.error(f"Error during initialization: {e}")
        raise


async def index_and_watch():
    """Index existing PDFs and start file watcher"""
    try:
        # Index existing PDFs
        await index_existing_pdfs()

        # Set up file watcher
        global file_watcher
        file_watcher = PDFWatcher()
        file_watcher.start(
            on_created=lambda path: asyncio.create_task(process_pdf_file(path)),
            on_modified=lambda path: asyncio.create_task(handle_modified(path)),
            on_deleted=lambda path: handle_deleted(path)
        )

        logger.info("File watcher started successfully")

    except Exception as e:
        logger.error(f"Error during indexing/watching: {e}")


if __name__ == "__main__":
    # Initialize components
    initialize()

    # Run the server (FastMCP will handle async initialization)
    mcp.run()
