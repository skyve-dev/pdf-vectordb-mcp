# Arsitektur 3-Tier: PDF Vector DB MCP Server

## Overview
Aplikasi ini menggunakan arsitektur berlapis (layered architecture) dengan 3 tier utama untuk pemisahan concerns yang jelas.

## Diagram Arsitektur Lengkap

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          TIER 1: PRESENTATION LAYER                         │
│                            (Interface dengan User)                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                       MCP Server (FastMCP)                          │  │
│  │                      src/mcp_server.py                              │  │
│  ├─────────────────────────────────────────────────────────────────────┤  │
│  │                                                                     │  │
│  │  @mcp.tool()                          @mcp.tool()                  │  │
│  │  ┌─────────────────┐                  ┌──────────────────┐         │  │
│  │  │ index_pdf()     │                  │ search_pdfs()    │         │  │
│  │  │ - Validasi input│                  │ - Validasi query │         │  │
│  │  │ - Call business │                  │ - Call business  │         │  │
│  │  │ - Format output │                  │ - Format results │         │  │
│  │  └─────────────────┘                  └──────────────────┘         │  │
│  │                                                                     │  │
│  │  @mcp.tool()         @mcp.tool()              @mcp.tool()          │  │
│  │  ┌──────────────┐   ┌────────────────┐       ┌─────────────┐      │  │
│  │  │ list_pdfs()  │   │ get_stats()    │       │ delete_pdf()│      │  │
│  │  └──────────────┘   └────────────────┘       └─────────────┘      │  │
│  │                                                                     │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│                                    │                                        │
│                                    │ Calls                                  │
│                                    ▼                                        │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                      TIER 2: BUSINESS LOGIC LAYER                           │
│                         (Logika Bisnis & Proses)                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────────────┐        ┌──────────────────────┐                 │
│  │   PDFProcessor       │        │  EmbeddingGenerator  │                 │
│  │ src/pdf_processor.py │        │  src/embeddings.py   │                 │
│  ├──────────────────────┤        ├──────────────────────┤                 │
│  │ • extract_text()     │        │ • generate()         │                 │
│  │ • chunk_text()       │        │ • load_model()       │                 │
│  │ • process_pdf()      │        │ • batch_generate()   │                 │
│  │                      │        │ • model caching      │                 │
│  │ PyPDF2 Integration   │        │ SentenceTransformer  │                 │
│  └──────────────────────┘        └──────────────────────┘                 │
│            │                                │                               │
│            │                                │                               │
│            └────────────┬───────────────────┘                               │
│                         │                                                   │
│                         │ Uses                                              │
│                         ▼                                                   │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐    │
│  │                        Utils Module                               │    │
│  │                      src/utils.py                                 │    │
│  ├───────────────────────────────────────────────────────────────────┤    │
│  │  • chunk_text() - Text chunking dengan overlap                    │    │
│  │  • generate_chunk_id() - ID generation untuk chunks               │    │
│  │  • compute_file_hash() - Hash calculation untuk tracking          │    │
│  │  • format_metadata() - Metadata formatting                        │    │
│  └───────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐    │
│  │                      FileWatcher                                  │    │
│  │                   src/file_watcher.py                             │    │
│  ├───────────────────────────────────────────────────────────────────┤    │
│  │  • start_watching() - Monitor file changes                        │    │
│  │  • on_created() - Handle new files                                │    │
│  │  • on_modified() - Handle file updates                            │    │
│  │  • debouncing logic - Prevent duplicate processing                │    │
│  │                                                                    │    │
│  │  Uses: watchdog library (Observer pattern)                        │    │
│  └───────────────────────────────────────────────────────────────────┘    │
│                                    │                                        │
│                                    │ Calls                                  │
│                                    ▼                                        │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                         TIER 3: DATA ACCESS LAYER                           │
│                      (Penyimpanan & Retrieval Data)                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                        VectorStore                                  │  │
│  │                     src/vector_store.py                             │  │
│  ├─────────────────────────────────────────────────────────────────────┤  │
│  │                                                                     │  │
│  │  CRUD Operations:                                                   │  │
│  │  • add_documents() - Insert vectors + metadata                     │  │
│  │  • search() - Query with similarity search                         │  │
│  │  • delete_document() - Remove by file_path                         │  │
│  │  • list_documents() - List all indexed files                       │  │
│  │  • get_stats() - Collection statistics                             │  │
│  │                                                                     │  │
│  │  ChromaDB Integration:                                              │  │
│  │  • Client initialization                                            │  │
│  │  • Collection management                                            │  │
│  │  • Persistent storage                                               │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                    │                                        │
│                                    │ Persists to                            │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                     ChromaDB Database                               │  │
│  │                  ./chroma_db/ (SQLite)                              │  │
│  ├─────────────────────────────────────────────────────────────────────┤  │
│  │                                                                     │  │
│  │  Collections:                                                       │  │
│  │  └─ pdf_documents                                                   │  │
│  │     ├─ Documents (text chunks)                                      │  │
│  │     ├─ Embeddings (768-dim vectors)                                 │  │
│  │     ├─ Metadata (file_path, page_num, chunk_id, etc)               │  │
│  │     └─ IDs (unique identifiers)                                     │  │
│  │                                                                     │  │
│  │  Storage Engine: SQLite + HNSW Index                                │  │
│  │  • Persistent on-disk storage                                       │  │
│  │  • Fast approximate nearest neighbor search                         │  │
│  │  • Automatic indexing                                               │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                        CROSS-CUTTING CONCERNS                               │
│                    (Komponen yang digunakan semua layer)                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐    │
│  │                      Configuration                                │    │
│  │                      src/config.py                                │    │
│  ├───────────────────────────────────────────────────────────────────┤    │
│  │  • Environment variables (from .env)                              │    │
│  │  • PDF_DIRECTORY                                                  │    │
│  │  • CHROMA_DB_PATH                                                 │    │
│  │  • EMBEDDING_MODEL                                                │    │
│  │  • CHUNK_SIZE, CHUNK_OVERLAP                                      │    │
│  │  • DEVICE (cpu/cuda)                                              │    │
│  │  • TOP_K (search results)                                         │    │
│  │                                                                    │    │
│  │  Used by: ALL components                                          │    │
│  └───────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Penjelasan Tier

### Tier 1: Presentation Layer
**Tanggung Jawab:**
- Menerima request dari Claude Desktop (MCP client)
- Validasi input dari user
- Format output untuk ditampilkan
- Handle errors dan exceptions
- Expose 5 tools via MCP protocol

**Karakteristik:**
- Tidak ada business logic
- Thin layer - hanya orchestration
- Async/await untuk non-blocking operations

### Tier 2: Business Logic Layer
**Tanggung Jawab:**
- Processing PDF (extraction, chunking)
- Generate embeddings dari text
- File watching dan auto-indexing
- Helper functions (hashing, ID generation)
- Business rules dan validations

**Karakteristik:**
- Tidak tahu tentang MCP protocol
- Reusable components
- Independent dari presentation layer
- Bisa di-test secara terpisah

### Tier 3: Data Access Layer
**Tanggung Jawab:**
- CRUD operations ke ChromaDB
- Vector similarity search
- Data persistence
- Collection management
- Query optimization

**Karakteristik:**
- Abstraksi database operations
- Hide ChromaDB implementation details
- Bisa diganti dengan vector DB lain tanpa ubah layer atas

## Aliran Data Antar Tier

### Request Flow (Top-Down)
```
Claude Desktop
     ↓
MCP Protocol (STDIO)
     ↓
Presentation Layer (mcp_server.py)
     ↓
Business Logic Layer (processors, embeddings)
     ↓
Data Access Layer (vector_store.py)
     ↓
ChromaDB (persistent storage)
```

### Response Flow (Bottom-Up)
```
ChromaDB (hasil query)
     ↓
Data Access Layer (format data)
     ↓
Business Logic Layer (process results)
     ↓
Presentation Layer (format untuk MCP)
     ↓
MCP Protocol (STDIO)
     ↓
Claude Desktop (tampil ke user)
```

## Keuntungan Arsitektur 3-Tier

### 1. Separation of Concerns
Setiap layer punya tanggung jawab yang jelas:
- Presentation: UI/Interface
- Business: Logic & Processing
- Data: Storage & Retrieval

### 2. Maintainability
- Mudah mencari bugs (tahu layer mana yang bermasalah)
- Mudah update satu komponen tanpa ganggu yang lain
- Code lebih organized dan readable

### 3. Testability
- Bisa test setiap layer secara terpisah
- Mock dependencies antar layer
- Unit test, integration test jadi mudah

### 4. Scalability
- Bisa scale setiap layer secara independent
- Misalnya: ChromaDB bisa dipindah ke server terpisah
- Atau: Bisa tambah load balancer di presentation layer

### 5. Reusability
- Business logic bisa dipakai oleh interface lain (tidak hanya MCP)
- Data layer bisa dipakai oleh aplikasi lain
- Components bisa di-share antar projects

## Dependency Flow

```
┌─────────────────┐
│  Presentation   │  ← Depends on Business Logic
└─────────────────┘
        ↓
┌─────────────────┐
│ Business Logic  │  ← Depends on Data Access
└─────────────────┘
        ↓
┌─────────────────┐
│  Data Access    │  ← Depends on Database
└─────────────────┘
        ↓
┌─────────────────┐
│    Database     │  ← No dependencies
└─────────────────┘
```

**Aturan Penting:**
- Layer atas bisa call layer bawah ✅
- Layer bawah TIDAK BOLEH call layer atas ❌
- Dependency hanya satu arah (top-down) ✅

## Contoh Implementasi Dependency Injection

```python
# src/mcp_server.py (Presentation Layer)
class MCPServer:
    def __init__(self):
        # Inject dependencies dari layer bawah
        self.config = Config()
        self.pdf_processor = PDFProcessor(self.config)
        self.embedding_generator = EmbeddingGenerator(self.config)
        self.vector_store = VectorStore(self.config)
        self.file_watcher = FileWatcher(
            self.config,
            self.pdf_processor,
            self.embedding_generator,
            self.vector_store
        )

    @mcp.tool()
    async def index_pdf(self, file_path: str):
        # Orchestration - delegate ke business logic
        result = self.pdf_processor.process_pdf(file_path)
        embeddings = await self.embedding_generator.generate(result['chunks'])
        self.vector_store.add_documents(embeddings, result['metadata'])
        return result
```

## Design Patterns yang Digunakan

1. **Layered Architecture** - Separasi 3 tier
2. **Dependency Injection** - Inject dependencies di constructor
3. **Façade Pattern** - VectorStore sebagai façade untuk ChromaDB
4. **Observer Pattern** - FileWatcher observe file system events
5. **Pipeline Pattern** - PDF processing pipeline (extract → chunk → embed → store)

