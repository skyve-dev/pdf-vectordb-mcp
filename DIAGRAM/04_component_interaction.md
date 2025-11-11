# Component Interaction Diagram

## Overview
Dokumen ini menjelaskan bagaimana setiap komponen berinteraksi satu sama lain dalam sistem PDF Vector DB MCP Server.

## Complete System Component Map

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            External Client                                  │
│                         (Claude Desktop App)                                │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       │ MCP Protocol (STDIO)
                                       │ JSON-RPC Communication
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│                          📋 MCP SERVER (FastMCP)                            │
│                             src/mcp_server.py                               │
│                                                                             │
│  ┌────────────────────────────────────────────────────────────────────┐   │
│  │                         Tool Endpoints                             │   │
│  │  • index_pdf()        • list_pdfs()                                │   │
│  │  • search_pdfs()      • get_stats()                                │   │
│  │  • delete_pdf()                                                    │   │
│  └────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│         │              │              │              │              │       │
│         │ uses         │ uses         │ uses         │ uses         │ uses  │
│         ▼              ▼              ▼              ▼              ▼       │
│  ┌──────────┐  ┌─────────────┐  ┌──────────┐  ┌───────────┐  ┌────────┐  │
│  │  Config  │  │PDFProcessor │  │Embedding │  │VectorStore│  │  File  │  │
│  │          │  │             │  │Generator │  │           │  │Watcher │  │
│  └──────────┘  └─────────────┘  └──────────┘  └───────────┘  └────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
         ▲                  │              │              │              │
         │ reads            │ uses         │ uses         │ accesses     │ monitors
         │                  ▼              ▼              ▼              ▼
┌────────┴────┐     ┌──────────┐  ┌──────────┐  ┌───────────┐  ┌────────────┐
│   .env      │     │  Utils   │  │   ML     │  │ ChromaDB  │  │File System │
│   File      │     │          │  │  Model   │  │           │  │   (PDFs)   │
└─────────────┘     └──────────┘  └──────────┘  └───────────┘  └────────────┘
                            │
                            │ provides utilities
                            └──────────────────────────┐
                                                       ▼
                                               (Used by multiple
                                                components)
```

## Detailed Component Interactions

### 1. MCP Server ↔ All Components

```
┌──────────────────────────────────────────────────────────────┐
│                    MCP Server (Orchestrator)                 │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Initialize all components:                                  │
│  ┌────────────────────────────────────────────────────┐     │
│  │  def __init__(self):                               │     │
│  │      self.config = Config()                        │     │
│  │      self.pdf_processor = PDFProcessor(config)     │     │
│  │      self.embedding_generator =                    │     │
│  │          EmbeddingGenerator(config)                │     │
│  │      self.vector_store = VectorStore(config)       │     │
│  │      self.file_watcher = FileWatcher(...)          │     │
│  └────────────────────────────────────────────────────┘     │
│                                                              │
│  Dependency Injection Pattern:                               │
│  • MCP Server creates all dependencies                      │
│  • Passes config to all components                          │
│  • Components don't know about MCP Server                   │
│  • One-way dependency (top-down) ✓                          │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 2. Config ↔ Environment

```
┌──────────────────────────────────────────────────────────────┐
│                         Config Component                     │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Load environment variables:                                 │
│  ┌────────────────────────────────────────────────────┐     │
│  │  from dotenv import load_dotenv                    │     │
│  │  import os                                          │     │
│  │                                                     │     │
│  │  load_dotenv()  # Read .env file                   │     │
│  │                                                     │     │
│  │  PDF_DIRECTORY = Path(                             │     │
│  │      os.getenv("PDF_DIRECTORY", "pdfs")           │     │
│  │  )                                                  │     │
│  │  CHUNK_SIZE = int(                                 │     │
│  │      os.getenv("CHUNK_SIZE", "1000")              │     │
│  │  )                                                  │     │
│  │  # ... other settings                              │     │
│  └────────────────────────────────────────────────────┘     │
│                                                              │
│  Used by: ALL components                                     │
│  • Single source of truth for configuration                 │
│  • Easy to change settings without code modification        │
│  • Environment-specific settings (dev/prod)                 │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 3. PDFProcessor ↔ Utils

```
┌──────────────────────────────────────────────────────────────┐
│                      PDFProcessor Component                  │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Uses Utils for helper functions:                            │
│                                                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │  from src.utils import (                           │     │
│  │      chunk_text,           # Text chunking         │     │
│  │      generate_chunk_id,    # ID generation         │     │
│  │      compute_file_hash     # File hashing          │     │
│  │  )                                                  │     │
│  │                                                     │     │
│  │  def process_pdf(self, pdf_path: Path):           │     │
│  │      # 1. Extract text                             │     │
│  │      text = self._extract_text(pdf_path)           │     │
│  │                                                     │     │
│  │      # 2. Use Utils.chunk_text                     │     │
│  │      chunks = chunk_text(                          │     │
│  │          text,                                      │     │
│  │          chunk_size=self.config.CHUNK_SIZE         │     │
│  │      )                                              │     │
│  │                                                     │     │
│  │      # 3. Use Utils.generate_chunk_id              │     │
│  │      for i, chunk in enumerate(chunks):            │     │
│  │          chunk_id = generate_chunk_id(             │     │
│  │              pdf_path, i                           │     │
│  │          )                                          │     │
│  │                                                     │     │
│  │      # 4. Use Utils.compute_file_hash              │     │
│  │      file_hash = compute_file_hash(pdf_path)       │     │
│  │                                                     │     │
│  │      return {                                       │     │
│  │          'chunks': chunks,                         │     │
│  │          'file_hash': file_hash,                   │     │
│  │          ...                                        │     │
│  │      }                                              │     │
│  └────────────────────────────────────────────────────┘     │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 4. EmbeddingGenerator ↔ ML Model

```
┌──────────────────────────────────────────────────────────────┐
│                  EmbeddingGenerator Component                │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Lazy loading of ML model:                                   │
│                                                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │  class EmbeddingGenerator:                         │     │
│  │      def __init__(self, config: Config):           │     │
│  │          self.config = config                      │     │
│  │          self.model = None  # Not loaded yet!      │     │
│  │                                                     │     │
│  │      def _load_model(self):                        │     │
│  │          """Load model on first use"""             │     │
│  │          if self.model is None:                    │     │
│  │              self.model = SentenceTransformer(     │     │
│  │                  self.config.EMBEDDING_MODEL,      │     │
│  │                  device=self.config.DEVICE         │     │
│  │              )                                      │     │
│  │                                                     │     │
│  │      async def generate(self, texts):              │     │
│  │          self._load_model()  # Load if needed      │     │
│  │          embeddings = self.model.encode(texts)     │     │
│  │          return embeddings.tolist()                │     │
│  └────────────────────────────────────────────────────┘     │
│                                                              │
│  Why lazy loading?                                           │
│  • Model is 420MB - expensive to load                       │
│  • Only load when actually needed                           │
│  • Reuse same model for all operations                      │
│  • Faster startup time                                      │
│                                                              │
│  Model caching:                                              │
│  • First call: Load model (~2-3 seconds)                    │
│  • Subsequent calls: Reuse loaded model (~50ms)             │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 5. VectorStore ↔ ChromaDB

```
┌──────────────────────────────────────────────────────────────┐
│                    VectorStore Component                     │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Façade pattern for ChromaDB:                                │
│                                                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │  import chromadb                                   │     │
│  │                                                     │     │
│  │  class VectorStore:                                │     │
│  │      def __init__(self, config: Config):           │     │
│  │          # Initialize ChromaDB client              │     │
│  │          self.client = chromadb.PersistentClient(  │     │
│  │              path=str(config.CHROMA_DB_PATH)       │     │
│  │          )                                          │     │
│  │                                                     │     │
│  │          # Get or create collection                │     │
│  │          self.collection = self.client.             │     │
│  │              get_or_create_collection(             │     │
│  │                  name="pdf_documents"               │     │
│  │              )                                      │     │
│  │                                                     │     │
│  │      def add_documents(self, docs):                │     │
│  │          """Abstraction over ChromaDB add"""       │     │
│  │          self.collection.add(                      │     │
│  │              ids=[d['id'] for d in docs],          │     │
│  │              documents=[d['text'] for d in docs],  │     │
│  │              embeddings=[d['emb'] for d in docs],  │     │
│  │              metadatas=[d['meta'] for d in docs]   │     │
│  │          )                                          │     │
│  │                                                     │     │
│  │      def search(self, query_embedding, k):         │     │
│  │          """Abstraction over ChromaDB query"""     │     │
│  │          return self.collection.query(             │     │
│  │              query_embeddings=[query_embedding],   │     │
│  │              n_results=k                           │     │
│  │          )                                          │     │
│  └────────────────────────────────────────────────────┘     │
│                                                              │
│  Why façade pattern?                                         │
│  • Hide ChromaDB implementation details                     │
│  • Easier to swap vector DB if needed                       │
│  • Cleaner API for other components                         │
│  • Centralized DB operations                                │
│                                                              │
└──────────────────────────────────────────────────────────────┘
                              │
                              │ Persists to
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                      ChromaDB Database                       │
│                    ./chroma_db/chroma.sqlite3                │
├──────────────────────────────────────────────────────────────┤
│  • SQLite backend (persistent storage)                       │
│  • HNSW index for fast similarity search                     │
│  • Automatic indexing on insert                              │
│  • Efficient vector operations                               │
└──────────────────────────────────────────────────────────────┘
```

### 6. FileWatcher ↔ File System + Other Components

```
┌──────────────────────────────────────────────────────────────┐
│                    FileWatcher Component                     │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Observer pattern with Watchdog library:                     │
│                                                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │  from watchdog.observers import Observer           │     │
│  │  from watchdog.events import FileSystemEventHandler│     │
│  │                                                     │     │
│  │  class FileWatcher(FileSystemEventHandler):        │     │
│  │      def __init__(self,                            │     │
│  │                   config,                          │     │
│  │                   pdf_processor,    ◄─┐            │     │
│  │                   embedding_gen,    ◄─┤ Injected   │     │
│  │                   vector_store):    ◄─┘            │     │
│  │          self.config = config                      │     │
│  │          self.pdf_processor = pdf_processor        │     │
│  │          self.embedding_gen = embedding_gen        │     │
│  │          self.vector_store = vector_store          │     │
│  │          self.observer = Observer()                │     │
│  │          self.processing = {}  # Debouncing        │     │
│  │                                                     │     │
│  │      def start_watching(self):                     │     │
│  │          """Start monitoring file system"""        │     │
│  │          self.observer.schedule(                   │     │
│  │              self,                                  │     │
│  │              path=str(self.config.PDF_DIRECTORY),  │     │
│  │              recursive=False                        │     │
│  │          )                                          │     │
│  │          self.observer.start()                     │     │
│  │                                                     │     │
│  │      def on_created(self, event):                  │     │
│  │          """File created event"""                  │     │
│  │          if event.src_path.endswith('.pdf'):       │     │
│  │              self._debounce_and_process(           │     │
│  │                  event.src_path                    │     │
│  │              )                                      │     │
│  │                                                     │     │
│  │      def _debounce_and_process(self, path):        │     │
│  │          """Prevent duplicate processing"""        │     │
│  │          if path in self.processing:               │     │
│  │              return  # Already processing          │     │
│  │                                                     │     │
│  │          self.processing[path] = True              │     │
│  │          time.sleep(1)  # Wait for file write      │     │
│  │                                                     │     │
│  │          # Use injected components                 │     │
│  │          result = self.pdf_processor.process_pdf(  │     │
│  │              Path(path)                            │     │
│  │          )                                          │     │
│  │          embeddings = self.embedding_gen.generate( │     │
│  │              result['chunks']                      │     │
│  │          )                                          │     │
│  │          self.vector_store.add_documents(          │     │
│  │              embeddings                            │     │
│  │          )                                          │     │
│  │                                                     │     │
│  │          del self.processing[path]                 │     │
│  └────────────────────────────────────────────────────┘     │
│                                                              │
│  Monitors: config.PDF_DIRECTORY                              │
│  Uses: PDFProcessor, EmbeddingGenerator, VectorStore         │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

## Sequence Diagram: Complete Index Flow

```
User      MCP         PDF        Utils    Embedding   Vector     ChromaDB
         Server    Processor            Generator    Store
  │         │          │           │         │          │           │
  │─index──▶│          │           │         │          │           │
  │         │          │           │         │          │           │
  │         │─process─▶│           │         │          │           │
  │         │          │           │         │          │           │
  │         │          │──extract──│         │          │           │
  │         │          │   text    │         │          │           │
  │         │          │           │         │          │           │
  │         │          │─chunk_text│         │          │           │
  │         │          │◀──────────┤         │          │           │
  │         │          │  chunks   │         │          │           │
  │         │          │           │         │          │           │
  │         │          │generate_  │         │          │           │
  │         │          │─chunk_id──┤         │          │           │
  │         │          │◀──────────┤         │          │           │
  │         │          │           │         │          │           │
  │         │          │compute_   │         │          │           │
  │         │          │─file_hash─┤         │          │           │
  │         │          │◀──────────┤         │          │           │
  │         │          │           │         │          │           │
  │         │◀─result──│           │         │          │           │
  │         │          │           │         │          │           │
  │         │──────────generate────────────▶│          │           │
  │         │          embeddings            │          │           │
  │         │◀─────────────────────────────│          │           │
  │         │          vectors               │          │           │
  │         │                                 │          │           │
  │         │─────────────────add_documents──────────▶│           │
  │         │                                 │          │           │
  │         │                                 │          │─add()───▶│
  │         │                                 │          │          │
  │         │                                 │          │◀─success─┤
  │         │                                 │          │           │
  │         │◀──────────────────────────────────────────┤           │
  │         │                                 │          │           │
  │◀success─│                                 │          │           │
  │         │                                 │          │           │
```

## Sequence Diagram: Complete Search Flow

```
User      MCP      Embedding   Vector     ChromaDB
         Server   Generator    Store
  │         │         │          │           │
  │─search─▶│         │          │           │
  │         │         │          │           │
  │         │──embed──▶          │           │
  │         │  query  │          │           │
  │         │         │          │           │
  │         │◀────────┤          │           │
  │         │  vector │          │           │
  │         │         │          │           │
  │         │────────search──────▶           │
  │         │         │          │           │
  │         │         │          │─query()──▶│
  │         │         │          │  (HNSW)   │
  │         │         │          │◀──────────┤
  │         │         │          │  results  │
  │         │◀───────────────────┤           │
  │         │       results      │           │
  │◀results─│         │          │           │
  │         │         │          │           │
```

## Dependency Graph

```
                    ┌─────────────┐
                    │   .env file │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │   Config    │◀────────────┐
                    └──────┬──────┘             │
                           │                    │
              ┌────────────┼────────────┐       │
              │            │            │       │
              ▼            ▼            ▼       │
       ┌──────────┐  ┌──────────┐  ┌──────────┐│
       │   PDF    │  │Embedding │  │  Vector  ││
       │Processor │  │Generator │  │  Store   ││
       └────┬─────┘  └──────────┘  └──────────┘│
            │                                   │
            │                                   │
            ▼                                   │
       ┌──────────┐                             │
       │  Utils   │                             │
       └──────────┘                             │
                                                │
              ┌─────────────────────────────────┤
              │                                 │
              ▼                                 │
       ┌─────────────┐                          │
       │ FileWatcher │──────────────────────────┘
       └──────┬──────┘
              │
              ▼
       (Uses: PDFProcessor,
        EmbeddingGenerator,
        VectorStore)
              │
              └─────────────────────┐
                                    │
                                    ▼
                            ┌──────────────┐
                            │  MCP Server  │
                            │ (Orchestrator)│
                            └──────────────┘
                                    ▲
                                    │
                            ┌───────┴───────┐
                            │ Claude Desktop│
                            └───────────────┘
```

**Dependency Rules:**
- Arrows point from dependent to dependency
- All components depend on Config
- MCP Server depends on all business logic components
- Utils is a pure utility (no dependencies on other components)
- One-way dependencies (no circular dependencies)

## Communication Patterns

### 1. Synchronous Calls
```
MCP Server → PDFProcessor.process_pdf()
             ↓
             Returns result immediately
```

### 2. Asynchronous Calls
```
MCP Server → await EmbeddingGenerator.generate()
             ↓
             Non-blocking, can handle multiple concurrent requests
```

### 3. Event-Driven
```
File System → Event (file created)
              ↓
              FileWatcher.on_created()
              ↓
              Auto-index PDF
```

### 4. Lazy Loading
```
EmbeddingGenerator → First call: Load model
                     ↓
                     Subsequent calls: Use cached model
```

## Error Propagation

```
ChromaDB Error
      ↓
VectorStore catches & wraps
      ↓
MCP Server catches
      ↓
Format user-friendly message
      ↓
Return to Claude Desktop
```

**Example:**
```python
try:
    self.vector_store.add_documents(docs)
except ChromaDBException as e:
    logger.error(f"Database error: {e}")
    return {
        "status": "error",
        "message": "Failed to store documents in database"
    }
```

## Component Lifecycle

### 1. Startup Sequence
```
1. Load Config (read .env)
2. Create MCP Server instance
3. Initialize components (lazy - don't load models yet)
4. Start FileWatcher (if enabled)
5. MCP Server ready to receive requests
```

### 2. First Request Handling
```
1. Receive index_pdf request
2. PDFProcessor: Extract & chunk
3. EmbeddingGenerator: Load model (first time)
4. EmbeddingGenerator: Generate embeddings
5. VectorStore: Store in ChromaDB
6. Return success
```

### 3. Subsequent Requests
```
1. Receive search_pdfs request
2. EmbeddingGenerator: Generate query embedding (model already loaded)
3. VectorStore: Query ChromaDB
4. Format and return results
```

### 4. Shutdown
```
1. FileWatcher: Stop observer
2. MCP Server: Close connections
3. ChromaDB: Persist data (automatic)
4. Clean exit
```

## Design Principles Applied

### 1. Single Responsibility Principle (SRP)
- Each component has ONE clear purpose
- PDFProcessor: Only PDF processing
- EmbeddingGenerator: Only embeddings
- VectorStore: Only database operations

### 2. Dependency Injection
- Components receive dependencies via constructor
- No hard-coded dependencies
- Easy to test with mocks

### 3. Façade Pattern
- VectorStore hides ChromaDB complexity
- Simple API for other components

### 4. Observer Pattern
- FileWatcher observes file system
- Reacts to events automatically

### 5. Lazy Loading
- Don't load resources until needed
- Faster startup, efficient memory use

## Summary

**Key Interaction Patterns:**
1. **Orchestration** - MCP Server coordinates all components
2. **Dependency Injection** - Components receive dependencies
3. **Façade** - VectorStore abstracts ChromaDB
4. **Observer** - FileWatcher monitors file system
5. **Lazy Loading** - Models loaded on first use

**Communication Flows:**
- **Top-Down** - MCP Server calls business logic
- **Horizontal** - Components use Utils
- **Event-Driven** - FileWatcher reacts to file events
- **Async** - Non-blocking operations for better performance

