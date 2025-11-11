# Architecture Documentation

This document explains the technical architecture and design decisions of the PDF Vector DB MCP Server.

## System Overview

The PDF Vector DB MCP Server is a RAG (Retrieval-Augmented Generation) system that enables LLMs to query PDF documents through semantic search. It implements the Model Context Protocol (MCP) to provide standardized tools for document retrieval.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      Claude / LLM Client                     │
└────────────────────────┬────────────────────────────────────┘
                         │ MCP Protocol
┌────────────────────────▼────────────────────────────────────┐
│                    MCP Server (stdio)                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Tool Handlers                            │  │
│  │  • query_documents   • list_documents                │  │
│  │  • get_document_info • reindex_document              │  │
│  │  • get_system_stats                                  │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
┌───────▼─────┐ ┌────▼─────┐ ┌────▼──────┐
│   PDF       │ │Embedding │ │  Vector   │
│  Processor  │ │Generator │ │   Store   │
└─────────────┘ └──────────┘ └───────────┘
        │             │             │
        │             │             │
┌───────▼─────┐ ┌────▼─────┐ ┌────▼──────┐
│   pypdf     │ │ OpenAI   │ │ ChromaDB  │
│ Text Extract│ │   API    │ │  (Local)  │
└─────────────┘ └──────────┘ └───────────┘
        │
┌───────▼─────┐
│    File     │
│   Watcher   │
│ (watchdog)  │
└─────────────┘
        │
┌───────▼─────┐
│ data/pdfs/  │
│  (Folder)   │
└─────────────┘
```

## Core Components

### 1. MCP Server (`mcp_server.py`)

**Responsibility**: Main entry point and orchestration layer

**Key Features**:
- Implements MCP protocol using stdio transport
- Registers and handles tool calls
- Coordinates between components
- Manages server lifecycle

**Tools Provided**:
- `query_documents`: Semantic search interface
- `list_documents`: Document inventory
- `get_document_info`: Detailed document metadata
- `reindex_document`: Manual re-processing trigger
- `get_system_stats`: System health and statistics

**Design Decisions**:
- Uses async/await for non-blocking operations
- Delegates complex logic to specialized modules
- Maintains minimal state (delegates to vector store)

### 2. PDF Processor (`pdf_processor.py`)

**Responsibility**: Extract and chunk text from PDF files

**Pipeline**:
```
PDF File → pypdf Reader → Page Extraction → Text Cleaning → Chunking → Metadata
```

**Key Features**:
- Page-by-page processing for memory efficiency
- Smart chunking with sentence boundary detection
- Fallback to word boundaries
- Metadata preservation (page numbers, document name)

**Chunking Strategy**:
- Default: 800 characters per chunk with 200 character overlap
- Attempts to break at sentence boundaries (. ! ?)
- Falls back to word boundaries if no sentence break found
- Maintains context through overlap

**Design Decisions**:
- **Why pypdf?**: Simple, pure Python, handles most PDFs well
- **Why character-based chunks?**: More predictable than token-based
- **Why overlap?**: Prevents context loss at boundaries

### 3. Embedding Generator (`embeddings.py`)

**Responsibility**: Generate vector embeddings using OpenAI API

**Key Features**:
- Batch processing (100 texts per API call)
- Automatic retry with exponential backoff
- Error handling and logging
- Connection validation

**API Integration**:
- Uses OpenAI's Python SDK
- Default model: `text-embedding-3-small` (1536 dimensions)
- Processes in batches to optimize API calls
- Maintains order of embeddings

**Design Decisions**:
- **Why OpenAI?**: High quality, well-tested, cost-effective
- **Why batch processing?**: Reduces API calls and latency
- **Why retry logic?**: Handles transient network failures
- **Why tenacity?**: Industry-standard retry library

### 4. Vector Store (`vector_store.py`)

**Responsibility**: Store and retrieve embeddings using ChromaDB

**Key Features**:
- Persistent storage on disk
- Cosine similarity search
- Metadata filtering
- CRUD operations (Create, Read, Update, Delete)

**Storage Schema**:
```python
{
    "id": "document.pdf::page_5::chunk_2",
    "embedding": [0.123, 0.456, ...],  # 1536 dimensions
    "document": "chunk text content",
    "metadata": {
        "document": "document.pdf",
        "page": 5,
        "chunk_index": 2,
        "total_chunks_on_page": 10
    }
}
```

**Design Decisions**:
- **Why ChromaDB?**: Simple, embeddable, good for local deployment
- **Why cosine similarity?**: Standard for embeddings, normalized
- **Why persistent client?**: Survives server restarts
- **ID format**: Hierarchical for easy document deletion

### 5. File Watcher (`file_watcher.py`)

**Responsibility**: Monitor PDF folder for file system changes

**Key Features**:
- Real-time file system monitoring using watchdog
- Event debouncing (2-second delay)
- Handles create, modify, delete events
- Filters for .pdf files only

**Event Flow**:
```
File System Event → Handler → Debounce → Callback → Processing
```

**Debouncing Logic**:
- Prevents multiple processing during file writes
- Waits 2 seconds of inactivity before processing
- Tracks per-file timestamps

**Design Decisions**:
- **Why watchdog?**: Cross-platform, reliable, well-maintained
- **Why debouncing?**: Files may be written in chunks
- **Why 2 seconds?**: Balance between responsiveness and stability

### 6. Configuration (`config.py`)

**Responsibility**: Centralized configuration management

**Key Features**:
- Environment variable loading
- Default value fallbacks
- Validation on startup
- Directory creation
- Type conversion

**Configuration Sources**:
1. Environment variables (`.env` file)
2. Default values (hardcoded)
3. Computed values (e.g., BASE_DIR)

**Design Decisions**:
- **Why python-dotenv?**: Standard for env var management
- **Why class-based?**: Easy to access, type-safe
- **Why validate?**: Fail fast on misconfiguration

### 7. Utilities (`utils.py`)

**Responsibility**: Shared helper functions

**Key Functions**:
- `setup_logging()`: Configure logging
- `get_file_hash()`: MD5 hash for change detection
- `create_chunk_id()`: Generate unique chunk identifiers
- `split_text_with_overlap()`: Core chunking logic
- `format_source_citation()`: Pretty-print sources

## Data Flow

### Indexing Flow

```
1. PDF Added to folder
   ↓
2. File Watcher detects event
   ↓
3. PDF Processor extracts text
   ↓
4. Text split into chunks
   ↓
5. Embedding Generator calls OpenAI
   ↓
6. Vector Store saves to ChromaDB
   ↓
7. Ready for queries
```

### Query Flow

```
1. LLM sends query via MCP
   ↓
2. MCP Server receives query_documents call
   ↓
3. Embedding Generator embeds query
   ↓
4. Vector Store searches ChromaDB
   ↓
5. Results sorted by similarity
   ↓
6. Format with source citations
   ↓
7. Return to LLM
```

## Design Patterns

### 1. Dependency Injection
Components receive dependencies through constructors:
```python
def __init__(self, api_key: str = None):
    self.api_key = api_key or Config.OPENAI_API_KEY
```

### 2. Single Responsibility
Each module has one clear purpose:
- PDFProcessor: PDF handling only
- EmbeddingGenerator: Embedding generation only
- VectorStore: Storage operations only

### 3. Error Handling
Consistent error handling throughout:
```python
try:
    operation()
    logger.info("Success")
except Exception as e:
    logger.error(f"Error: {e}")
    raise
```

### 4. Async/Await
Non-blocking operations where appropriate:
```python
async def query_documents(self, query: str):
    # Async operations
```

## Performance Considerations

### Embedding Generation
- **Batch Size**: 100 texts per API call
- **Optimization**: Reduces API overhead by 100x
- **Trade-off**: Slight increase in latency for batch

### Vector Search
- **Index Type**: HNSW (Hierarchical Navigable Small World)
- **Similarity**: Cosine (faster than L2 for normalized vectors)
- **Top-K**: Default 5 results (configurable)

### Memory Management
- **Streaming**: Process PDFs page-by-page
- **Garbage Collection**: Python's GC handles cleanup
- **ChromaDB**: Persistence prevents memory buildup

### Disk I/O
- **ChromaDB Storage**: Append-only for safety
- **PDF Reading**: Buffered I/O via pypdf
- **Logs**: Async logging to reduce blocking

## Security Considerations

### API Keys
- Stored in `.env` file (not committed)
- Loaded at runtime only
- Never logged or exposed

### File Access
- Restricted to configured PDF folder
- No path traversal vulnerabilities
- Validates file extensions

### Input Validation
- Query length limits (handled by OpenAI)
- Metadata sanitization
- Error message sanitization (no stack traces to user)

## Scalability

### Current Limitations
- Single process (no parallelization)
- Local ChromaDB (no distributed setup)
- One folder watch only

### Future Scaling Options
1. **Horizontal**: Multiple servers with shared ChromaDB
2. **Vertical**: Increase chunk size, batch size
3. **Distributed**: Move to Qdrant/Pinecone cloud
4. **Caching**: Add Redis for frequent queries

## Testing Strategy

### Unit Tests
- Test individual functions in `utils.py`
- Mock external dependencies (OpenAI, ChromaDB)
- Fast, deterministic

### Integration Tests
- Test component interactions
- Use test PDFs
- Temporary ChromaDB instances

### Manual Testing
- Add sample PDFs
- Test all MCP tools
- Verify file watching

## Error Recovery

### Transient Failures
- **OpenAI API**: Retry with exponential backoff
- **File I/O**: Log and skip corrupted files
- **Network**: Automatic retry (tenacity)

### Permanent Failures
- **Invalid PDF**: Log error, skip file
- **No API Key**: Fail fast on startup
- **Disk Full**: Log error, alert user

## Monitoring and Logging

### Log Levels
- **DEBUG**: Detailed operation info
- **INFO**: Normal operations (default)
- **WARNING**: Recoverable errors
- **ERROR**: Failures requiring attention

### Log Destinations
- **Console**: Real-time feedback
- **File**: Persistent log (pdf_vectordb_mcp.log)

### Metrics to Monitor
- Total documents indexed
- Total chunks stored
- Query response times
- OpenAI API costs
- Disk usage

## Future Improvements

### Technical Debt
- Add comprehensive test suite
- Implement health check endpoint
- Add metrics collection (Prometheus)
- Add query caching

### Feature Additions
- OCR for scanned PDFs (tesseract)
- Table extraction (camelot)
- Multi-format support (Word, HTML)
- Hybrid search (vector + keyword)

### Performance
- Parallel PDF processing
- Embedding caching
- Query result caching
- Database connection pooling

## References

- [MCP Specification](https://modelcontextprotocol.io/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [OpenAI Embeddings Guide](https://platform.openai.com/docs/guides/embeddings)
- [pypdf Documentation](https://pypdf.readthedocs.io/)
