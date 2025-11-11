"""
Vector store module using ChromaDB
"""
import logging
from typing import List, Dict, Optional
from pathlib import Path
import chromadb
from chromadb.config import Settings
from .config import Config

logger = logging.getLogger(__name__)

class VectorStore:
    """Handles vector storage and retrieval using ChromaDB"""

    def __init__(self, persist_directory: Optional[Path] = None, collection_name: Optional[str] = None):
        """
        Initialize vector store

        Args:
            persist_directory: Directory for ChromaDB persistence (defaults to Config.CHROMA_DB_PATH)
            collection_name: Name of the collection (defaults to Config.COLLECTION_NAME)
        """
        self.persist_directory = persist_directory or Config.CHROMA_DB_PATH
        self.collection_name = collection_name or Config.COLLECTION_NAME

        # Initialize ChromaDB client with persistence
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(
                anonymized_telemetry=False
            )
        )

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}  # Use cosine similarity
        )

        logger.info(f"Initialized VectorStore with collection: {self.collection_name}")
        logger.info(f"Current collection size: {self.collection.count()} documents")

    def add_chunks(self, chunks: List[Dict], embeddings: List[List[float]]) -> None:
        """
        Add chunks with embeddings to the vector store

        Args:
            chunks: List of chunk dictionaries with 'id', 'text', and 'metadata'
            embeddings: List of embedding vectors corresponding to chunks
        """
        try:
            ids = [chunk['id'] for chunk in chunks]
            documents = [chunk['text'] for chunk in chunks]
            metadatas = [chunk['metadata'] for chunk in chunks]

            self.collection.add(
                ids=ids,
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas
            )

            logger.info(f"Added {len(chunks)} chunks to vector store")

        except Exception as e:
            logger.error(f"Error adding chunks to vector store: {e}")
            raise

    def query(self, query_embedding: List[float], top_k: int = None,
              filter_dict: Optional[Dict] = None) -> Dict:
        """
        Query the vector store with an embedding

        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return (defaults to Config.DEFAULT_TOP_K)
            filter_dict: Optional metadata filters (e.g., {"document": "example.pdf"})

        Returns:
            Dictionary containing results with documents, metadatas, and distances
        """
        try:
            top_k = top_k or Config.DEFAULT_TOP_K

            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=filter_dict
            )

            logger.info(f"Query returned {len(results['ids'][0])} results")
            return results

        except Exception as e:
            logger.error(f"Error querying vector store: {e}")
            raise

    def delete_by_document(self, document_name: str) -> None:
        """
        Delete all chunks belonging to a specific document

        Args:
            document_name: Name of the document to delete
        """
        try:
            self.collection.delete(
                where={"document": document_name}
            )
            logger.info(f"Deleted all chunks for document: {document_name}")

        except Exception as e:
            logger.error(f"Error deleting document {document_name}: {e}")
            raise

    def list_documents(self) -> List[Dict]:
        """
        List all unique documents in the vector store with statistics

        Returns:
            List of dictionaries containing document info
        """
        try:
            # Get all items
            results = self.collection.get()

            # Extract unique documents and count chunks
            doc_stats = {}
            for metadata in results['metadatas']:
                doc_name = metadata.get('document', 'Unknown')
                if doc_name not in doc_stats:
                    doc_stats[doc_name] = {
                        'document': doc_name,
                        'num_chunks': 0,
                        'pages': set()
                    }
                doc_stats[doc_name]['num_chunks'] += 1
                doc_stats[doc_name]['pages'].add(metadata.get('page', 0))

            # Convert to list and format
            documents = []
            for doc_name, stats in doc_stats.items():
                documents.append({
                    'document': doc_name,
                    'num_chunks': stats['num_chunks'],
                    'num_pages': len(stats['pages'])
                })

            logger.info(f"Found {len(documents)} unique documents")
            return documents

        except Exception as e:
            logger.error(f"Error listing documents: {e}")
            raise

    def get_document_info(self, document_name: str) -> Optional[Dict]:
        """
        Get detailed information about a specific document

        Args:
            document_name: Name of the document

        Returns:
            Dictionary with document information or None if not found
        """
        try:
            results = self.collection.get(
                where={"document": document_name}
            )

            if not results['ids']:
                return None

            # Calculate statistics
            pages = set()
            for metadata in results['metadatas']:
                pages.add(metadata.get('page', 0))

            return {
                'document': document_name,
                'num_chunks': len(results['ids']),
                'num_pages': len(pages),
                'pages': sorted(list(pages))
            }

        except Exception as e:
            logger.error(f"Error getting document info for {document_name}: {e}")
            raise

    def clear_collection(self) -> None:
        """Delete all documents in the collection"""
        try:
            # Delete the collection and recreate it
            self.client.delete_collection(self.collection_name)
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"Cleared collection: {self.collection_name}")

        except Exception as e:
            logger.error(f"Error clearing collection: {e}")
            raise

    def get_stats(self) -> Dict:
        """
        Get overall statistics about the vector store

        Returns:
            Dictionary with statistics
        """
        try:
            total_chunks = self.collection.count()
            documents = self.list_documents()

            return {
                'total_chunks': total_chunks,
                'total_documents': len(documents),
                'documents': documents
            }

        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            raise
