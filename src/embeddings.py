"""
Embedding generation module using sentence-transformers (local, no API key required)
"""
import logging
from typing import List
import torch
from sentence_transformers import SentenceTransformer
from .config import Config

logger = logging.getLogger(__name__)

class EmbeddingGenerator:
    """Handles embedding generation using sentence-transformers (all-mpnet-base-v2)"""

    def __init__(self, model_name: str = None, device: str = None):
        """
        Initialize embedding generator

        Args:
            model_name: Model name from sentence-transformers (defaults to Config.EMBEDDING_MODEL)
            device: Device to use - 'cpu', 'cuda', or 'auto' (defaults to Config.EMBEDDING_DEVICE)
        """
        self.model_name = model_name or Config.EMBEDDING_MODEL
        self.device = device or Config.EMBEDDING_DEVICE

        # Auto-detect device if set to 'auto'
        if self.device == 'auto':
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'

        logger.info(f"Initializing EmbeddingGenerator with model: {self.model_name}")
        logger.info(f"Using device: {self.device}")

        # Load the model
        try:
            self.model = SentenceTransformer(self.model_name, device=self.device)
            logger.info(f"Successfully loaded model: {self.model_name}")
            logger.info(f"Embedding dimension: {self.model.get_sentence_embedding_dimension()}")
        except Exception as e:
            logger.error(f"Error loading model {self.model_name}: {e}")
            raise

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text

        Args:
            text: Input text

        Returns:
            Embedding vector as list of floats
        """
        try:
            # encode returns numpy array, convert to list
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding.tolist()

        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise

    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in a batch

        Args:
            texts: List of input texts

        Returns:
            List of embedding vectors
        """
        try:
            # Process in batches for memory efficiency
            batch_size = 32  # Good balance between speed and memory

            logger.info(f"Processing {len(texts)} texts in batches of {batch_size}")

            # encode handles batching internally with show_progress_bar
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=True,
                convert_to_numpy=True
            )

            # Convert numpy arrays to lists
            embeddings_list = [emb.tolist() for emb in embeddings]

            logger.info(f"Generated {len(embeddings_list)} embeddings")
            return embeddings_list

        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            raise

    def embed_chunks(self, chunks: List[dict]) -> List[dict]:
        """
        Generate embeddings for a list of chunk dictionaries

        Args:
            chunks: List of chunk dictionaries with 'text' field

        Returns:
            Same chunks with 'embedding' field added
        """
        try:
            # Extract texts
            texts = [chunk['text'] for chunk in chunks]

            # Generate embeddings
            embeddings = self.generate_embeddings_batch(texts)

            # Add embeddings to chunks
            for chunk, embedding in zip(chunks, embeddings):
                chunk['embedding'] = embedding

            return chunks

        except Exception as e:
            logger.error(f"Error embedding chunks: {e}")
            raise

    def validate_connection(self) -> bool:
        """
        Validate that the model works

        Returns:
            True if model is functional, False otherwise
        """
        try:
            test_embedding = self.generate_embedding("test")
            return len(test_embedding) > 0
        except Exception as e:
            logger.error(f"Failed to validate local model: {e}")
            return False

    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of embeddings produced by this model

        Returns:
            Embedding dimension
        """
        return self.model.get_sentence_embedding_dimension()
