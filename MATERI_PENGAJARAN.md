# MATERI PENGAJARAN: PDF VECTOR DB MCP SERVER

**Target:** Mahasiswa/Pelajar dengan basic Python knowledge
**Durasi:** 6-8 Sesi (@ 2-3 jam)
**Prerequisites:** Python dasar, basic understanding databases

---

## 📚 MODUL 1: Pengenalan RAG dan Vector Search

### 1.1. Masalah yang Ingin Diselesaikan

**Skenario Real-World:**

Bayangkan Anda adalah seorang mahasiswa dengan 50 buku PDF untuk ujian akhir:
- Python Programming (500 halaman)
- Data Structures (400 halaman)
- Algorithms (600 halaman)
- ... dan 47 buku lainnya

**Pertanyaan:** "Bagaimana cara implement Binary Search Tree di Python?"

**Tanpa RAG:**
```
1. Buka buku Data Structures.pdf
2. Lihat index/table of contents
3. Cari "Binary Search Tree"
4. Baca chapter tersebut (20+ halaman)
5. Cari contoh Python code
6. Ulangi untuk buku lain jika tidak ketemu
⏰ Waktu: 30-60 menit!
```

**Dengan RAG:**
```
1. Tanya: "How to implement Binary Search Tree in Python?"
2. Sistem cari di 50 buku secara otomatis
3. Tampilkan hasil relevan dengan citation
⏰ Waktu: 5 detik!
```

### 1.2. Apa itu RAG?

**RAG = Retrieval-Augmented Generation**

Analogi sederhana:
```
┌─────────────────────────────────────┐
│  LLM Tanpa RAG                      │
├─────────────────────────────────────┤
│  Seperti murid ujian TANPA catatan  │
│  Hanya mengandalkan ingatan         │
│  Knowledge terbatas & outdated      │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  LLM Dengan RAG                     │
├─────────────────────────────────────┤
│  Seperti murid ujian DENGAN catatan │
│  Bisa cek informasi saat butuh      │
│  Knowledge unlimited & up-to-date   │
└─────────────────────────────────────┘
```

**3 Komponen RAG:**

1. **Retrieval (Pengambilan)**
   - Cari informasi relevan dari knowledge base
   - Berdasarkan semantic similarity, bukan keyword

2. **Augmentation (Penambahan)**
   - Gabungkan informasi yang ditemukan dengan pertanyaan
   - Berikan context ke LLM

3. **Generation (Pembuatan)**
   - LLM generate jawaban berdasarkan context
   - Lebih akurat karena punya informasi spesifik

**Contoh Workflow:**

```
User: "Apa keuntungan Python dibanding Java?"

1. RETRIEVAL:
   System cari di knowledge base:
   - Found: "Python has simpler syntax..." (python-intro.pdf)
   - Found: "Java requires more boilerplate..." (java-guide.pdf)
   - Found: "Python is interpreted, Java compiled..." (comparison.pdf)

2. AUGMENTATION:
   Context = User Question + Retrieved Info
   "Pertanyaan: Apa keuntungan Python dibanding Java?

    Context dari dokumen:
    1. Python has simpler syntax (python-intro.pdf, hal 5)
    2. Java requires more boilerplate (java-guide.pdf, hal 12)
    3. Python is interpreted, Java compiled (comparison.pdf, hal 23)"

3. GENERATION:
   LLM (Claude): "Berdasarkan dokumentasi:

   Keuntungan Python dibanding Java:
   1. Syntax lebih sederhana dan readable
   2. Less boilerplate code
   3. Faster development (interpreted)
   4. ...

   (Sumber: python-intro.pdf hal 5, java-guide.pdf hal 12)"
```

### 1.3. Konsep: Vector Embeddings

**Pertanyaan Fundamental:**

Komputer tidak mengerti text. Bagaimana komputer bisa "paham" makna kalimat?

**Jawaban:** Konversi text menjadi numbers (vectors)!

**Analogi:**

Imagine setiap kata/kalimat punya koordinat di peta:
```
"Kucing" → koordinat (3, 5)
"Anjing" → koordinat (4, 6)
"Mobil"  → koordinat (15, 2)
```

Kata dengan makna mirip → koordinat berdekatan:
- "Kucing" dan "Anjing" dekat (sama-sama hewan)
- "Mobil" jauh dari keduanya (bukan hewan)

**Real Embeddings:**

Tapi bukan 2D (x, y), melainkan 768D!
```
Text: "Kucing adalah hewan peliharaan"
       ↓ [Embedding Model]
Embedding: [0.234, -0.567, 0.123, ..., 0.891]
           ↑_____________768 angka_____________↑
```

**Mengapa 768 dimensi?**
- Lebih banyak dimensi = lebih detail
- Bisa tangkap nuances semantic
- Balance antara quality dan efficiency

**Semantic Similarity:**

```python
# Example (simplified to 3D for illustration):

emb1 = [0.5, 0.8, 0.1]  # "Mobil saya merah"
emb2 = [0.6, 0.7, 0.15] # "Kendaraan saya merah"
emb3 = [0.1, 0.2, 0.9]  # "Langit berwarna biru"

# Similarity (cosine):
similarity(emb1, emb2) = 0.95  # Very similar! (Mobil ≈ Kendaraan)
similarity(emb1, emb3) = 0.23  # Not similar (Mobil ≠ Langit)
```

**Visualisasi 2D (Simplified):**

```
    ^
    |
 0.9|                            • Langit biru
    |
 0.8|      • Mobil merah
 0.7|      • Kendaraan merah
    |
 0.5|
    |
    +--------------------------------->
       0.1       0.5       0.9
```

Mobil dan Kendaraan berdekatan (makna mirip)
Langit jauh (makna berbeda)

### 1.4. Vector Database

**Regular Database vs Vector Database:**

```
┌─────────────────────────────────────────────────────────┐
│  REGULAR DATABASE (SQL, NoSQL)                          │
├─────────────────────────────────────────────────────────┤
│  Query: WHERE title LIKE '%python%'                     │
│  Match: Exact keyword match                             │
│  Result: Documents dengan kata "python"                 │
│                                                          │
│  Problem: Miss "Python", "PYTHON", "py", synonyms       │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  VECTOR DATABASE (ChromaDB, Pinecone, Weaviate)        │
├─────────────────────────────────────────────────────────┤
│  Query: [0.234, -0.567, ..., 0.891]  (embedding)       │
│  Match: Semantic similarity                             │
│  Result: Documents dengan MAKNA mirip                   │
│                                                          │
│  Benefit: Find "Python", "py", "coding in Python", etc │
└─────────────────────────────────────────────────────────┘
```

**Contoh Real:**

```
Query: "How to loop in Python?"
Embedding: [0.2, 0.5, 0.8, ...]

Vector DB mencari chunks dengan embedding mirip:
✅ Found: "Python loops using for and while..." (similarity: 0.92)
✅ Found: "Iterate through lists in Python..." (similarity: 0.87)
✅ Found: "Python for loop syntax: for i in..." (similarity: 0.85)
❌ Tidak return: "Python history" (similarity: 0.23)
❌ Tidak return: "Install Python" (similarity: 0.31)
```

**Algoritma: HNSW (Hierarchical Navigable Small World)**

```
Tanpa HNSW (Brute Force):
  Compare query dengan SEMUA vectors
  Time: O(n) → Slow untuk millions vectors!

  Query vector
    ↓ compare
  Vector 1 → similarity 0.23
  Vector 2 → similarity 0.89  ✅
  Vector 3 → similarity 0.12
  ...
  Vector 1,000,000 → similarity 0.55

Dengan HNSW:
  Navigate graph structure
  Time: O(log n) → Fast!

  Query vector
    ↓
  Layer 3 (coarse) → Point to promising area
    ↓
  Layer 2 (medium) → Refine search
    ↓
  Layer 1 (fine)   → Get exact results

  Trade-off: 99% accuracy, 100x faster!
```

### 1.5. Quiz Modul 1

**Pertanyaan:**

1. Apa perbedaan utama RAG dengan LLM biasa?
2. Mengapa kita perlu convert text ke embeddings?
3. Apa keuntungan semantic search dibanding keyword search?
4. Jelaskan dengan kata-kata sendiri: apa itu vector database?
5. Berikan contoh use case RAG selain academic documents.

**Diskusi:**
- Kapan RAG lebih baik dari fine-tuning LLM?
- Apa limitations dari RAG system?

---

## 🏗️ MODUL 2: Arsitektur Aplikasi

### 2.1. High-Level Architecture

**Big Picture:**

```
┌─────────────────────────────────────────────────────────────┐
│                      CLAUDE DESKTOP                         │
│                     (MCP Client)                            │
│                                                              │
│  User bertanya → Claude memutuskan use tool → Call MCP      │
└─────────────────────────────────────────────────────────────┘
                            ↕
              [MCP Protocol via stdio]
                            ↕
┌─────────────────────────────────────────────────────────────┐
│              PDF VECTOR DB MCP SERVER                       │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ PRESENTATION LAYER (MCP Tools)                      │   │
│  │ • query_documents()                                 │   │
│  │ • list_documents()                                  │   │
│  │ • get_document_info()                               │   │
│  └─────────────────────────────────────────────────────┘   │
│                            ↕                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ BUSINESS LOGIC LAYER                                │   │
│  │ • PDFProcessor (extract & chunk)                    │   │
│  │ • EmbeddingGenerator (generate embeddings)          │   │
│  │ • PDFWatcher (monitor files)                        │   │
│  └─────────────────────────────────────────────────────┘   │
│                            ↕                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ DATA LAYER                                          │   │
│  │ • VectorStore (ChromaDB interface)                  │   │
│  │ • ChromaDB (vector database)                        │   │
│  │ • File System (PDF storage)                         │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│         SENTENCE-TRANSFORMERS (all-mpnet-base-v2)          │
│                                                              │
│  Embedding model yang runs locally (CPU/GPU)                │
└─────────────────────────────────────────────────────────────┘
```

### 2.2. Layered Architecture

**Mengapa Berlapis?**

Analogi: Organisasi perusahaan
```
CEO (Presentation)
  ↓ kasih instruksi
Managers (Business Logic)
  ↓ kasih instruksi
Workers (Data Layer)

Each layer punya responsibility sendiri!
```

**Layer 1: Presentation (Interface)**
```python
Role: Komunikasi dengan Claude Desktop

@mcp.tool()
def query_documents(query: str) -> str:
    # Simple interface
    # Tidak ada logic kompleks di sini
    # Just orchestrate
    pass

Analogi: Resepsionis hotel
- Terima request dari guest
- Delegate ke department lain
- Return response ke guest
```

**Layer 2: Business Logic (Processing)**
```python
Role: Processing dan transformations

class PDFProcessor:
    def extract_text(self):
        # Complex logic here
        pass

class EmbeddingGenerator:
    def generate_embeddings(self):
        # Complex logic here
        pass

Analogi: Chefs di kitchen
- Actual work happens here
- Implement business rules
- Transform data
```

**Layer 3: Data (Storage)**
```python
Role: Data persistence dan retrieval

class VectorStore:
    def add_chunks(self):
        # Save to database
        pass

    def query(self):
        # Retrieve from database
        pass

Analogi: Warehouse
- Store data safely
- Retrieve when needed
- Manage persistence
```

**Keuntungan Layered Architecture:**

1. **Separation of Concerns**
   ```
   Presentation → Fokus pada API
   Business     → Fokus pada logic
   Data         → Fokus pada storage

   Each layer bisa dikembangkan independently!
   ```

2. **Easy Testing**
   ```python
   # Test business logic tanpa database
   mock_vector_store = Mock()
   processor = PDFProcessor(vector_store=mock_vector_store)
   ```

3. **Maintainability**
   ```
   Change database? → Only touch Data Layer
   Change API?      → Only touch Presentation Layer
   Change logic?    → Only touch Business Layer
   ```

4. **Scalability**
   ```
   Bisa deploy layers ke servers berbeda:
   Presentation → Server A
   Business     → Server B (with GPU!)
   Data         → Server C (with SSD!)
   ```

### 2.3. Data Flow

**Flow 1: Indexing (PDF → Database)**

```
1. USER ACTION
   └─► Drag PDF to data/pdfs/

2. FILE DETECTION
   └─► PDFWatcher detects new file

3. EXTRACTION
   └─► PDFProcessor.extract_text_from_pdf()
       Input:  document.pdf
       Output: [
         {page: 1, text: "..."},
         {page: 2, text: "..."},
         ...
       ]

4. CHUNKING
   └─► PDFProcessor.chunk_pages()
       Input:  Pages data
       Output: [
         {id: "doc::p1::c0", text: "...", metadata: {...}},
         {id: "doc::p1::c1", text: "...", metadata: {...}},
         ...
       ]

5. EMBEDDING
   └─► EmbeddingGenerator.embed_chunks()
       Input:  Chunks
       Output: Chunks + embeddings
       [
         {text: "...", embedding: [0.1, 0.2, ..., 0.8]},
         ...
       ]

6. STORAGE
   └─► VectorStore.add_chunks()
       Input:  Chunks dengan embeddings
       Action: Save to ChromaDB
       Result: ✓ Indexed!
```

**Flow 2: Querying (Question → Answer)**

```
1. USER QUESTION
   └─► "How to create function in Python?"

2. TOOL CALL
   └─► Claude calls: query_documents(query="...")

3. EMBED QUERY
   └─► EmbeddingGenerator.generate_embedding(query)
       Input:  "How to create function in Python?"
       Output: [0.2, 0.5, ..., 0.8]  (768-dim vector)

4. SEARCH
   └─► VectorStore.query(query_embedding)
       Action: ChromaDB searches similar vectors
       Output: [
         {text: "...", distance: 0.23, metadata: {...}},
         {text: "...", distance: 0.34, metadata: {...}},
         ...
       ]

5. FORMAT
   └─► Format results dengan citations
       Output: """
         Ditemukan 5 hasil:

         --- Hasil 1 ---
         Sumber: python.pdf (Hal 45)
         Relevansi: 77%

         Functions are defined with def...
         """

6. RESPONSE
   └─► Return ke Claude → Claude generate answer
```

### 2.4. Component Interaction

**Skenario: User Add New PDF**

```
┌──────────┐
│ User     │ Drag python.pdf to data/pdfs/
└────┬─────┘
     │
     ↓ File System Event
┌────────────────┐
│ PDFWatcher     │ Detects new file
│ (file_watcher) │ Debounces (wait 2 sec)
└────┬───────────┘
     │
     ↓ Callback: process_pdf_file(path)
┌─────────────────┐
│ mcp_server.py   │ Orchestrates processing
└────┬────────────┘
     │
     ├─► ┌──────────────┐
     │   │ PDFProcessor │ Extract & chunk
     │   └──────────────┘
     │   Returns: chunks
     │
     ├─► ┌─────────────────────┐
     │   │ EmbeddingGenerator  │ Generate embeddings
     │   └─────────────────────┘
     │   Returns: chunks + embeddings
     │
     └─► ┌──────────────┐
         │ VectorStore  │ Save to ChromaDB
         └──────────────┘
         Result: ✓ Indexed!
```

### 2.5. Quiz Modul 2

**Pertanyaan:**

1. Sebutkan 3 layers dalam aplikasi ini dan responsibility masing-masing
2. Mengapa kita perlu separate layers?
3. Jelaskan data flow dari PDF file sampai tersimpan di database
4. Jelaskan data flow dari user query sampai mendapat answer
5. Component mana yang bertanggung jawab untuk monitoring files?

**Latihan:**

Draw diagram untuk skenario:
- User modify existing PDF
- User delete PDF
- User query specific document

---

## 💻 MODUL 3: Komponen Detail

### 3.1. Config (src/config.py)

**Purpose:** Centralized configuration management

**Konsep Penting:** Environment Variables

**Mengapa Environment Variables?**

```
❌ BAD: Hardcode di code
```python
CHUNK_SIZE = 800  # What if I want 1000?
PDF_FOLDER = "C:/Users/arif/pdfs"  # Different per developer!
```

✅ GOOD: Environment variables
```python
# .env file
CHUNK_SIZE=800
PDF_FOLDER=./data/pdfs

# Python code
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "800"))
# If env var exists → use it
# If not → use default 800
```

**Benefits:**
- Easy change settings tanpa modify code
- Different settings per environment (dev, test, prod)
- Secure (credentials tidak di code)

**Code Walkthrough:**

```python
import os
from pathlib import Path
from dotenv import load_dotenv

# Load dari .env file
load_dotenv()

class Config:
    # Embedding settings
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-mpnet-base-v2")
    EMBEDDING_DEVICE = os.getenv("EMBEDDING_DEVICE", "auto")

    # Paths
    BASE_DIR = Path(__file__).parent.parent  # Project root
    PDF_FOLDER = Path(os.getenv("PDF_FOLDER", BASE_DIR / "data" / "pdfs"))
    CHROMA_DB_PATH = Path(os.getenv("CHROMA_DB_PATH", BASE_DIR / "data" / "chroma_db"))

    # Chunking
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "800"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))

    # Retrieval
    DEFAULT_TOP_K = int(os.getenv("DEFAULT_TOP_K", "5"))

    @classmethod
    def validate(cls):
        """Validate settings dan create directories"""
        # Validations
        if cls.CHUNK_SIZE < 100:
            raise ValueError("CHUNK_SIZE too small!")

        if cls.CHUNK_OVERLAP >= cls.CHUNK_SIZE:
            raise ValueError("CHUNK_OVERLAP must be < CHUNK_SIZE!")

        # Create directories
        cls.PDF_FOLDER.mkdir(parents=True, exist_ok=True)
        cls.CHROMA_DB_PATH.mkdir(parents=True, exist_ok=True)
```

**Key Concepts:**

1. **Class Methods (@classmethod)**
   ```python
   @classmethod
   def validate(cls):
       # cls = Config class itself
       # No need to create instance!
       cls.CHUNK_SIZE  # Access class attributes

   # Usage:
   Config.validate()  # No Config() needed
   ```

2. **Path Management**
   ```python
   BASE_DIR = Path(__file__).parent.parent
   # __file__  = path to config.py
   # .parent   = src/
   # .parent   = project root/

   PDF_FOLDER = BASE_DIR / "data" / "pdfs"
   # Path objects can be joined with /
   ```

3. **Type Conversion**
   ```python
   # os.getenv() always returns string!
   chunk_size_str = os.getenv("CHUNK_SIZE", "800")  # "800" (string)
   chunk_size_int = int(chunk_size_str)              # 800 (integer)

   # Shorthand:
   CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "800"))
   ```

**Exercise:**

1. Add new config: `MAX_FILE_SIZE` (default: 100MB)
2. Validate: file size must be > 0
3. Add to get_summary()

### 3.2. Utils (src/utils.py)

**Purpose:** Helper functions yang digunakan di banyak tempat

**Function 1: split_text_with_overlap()**

```python
def split_text_with_overlap(text: str, chunk_size: int, overlap: int) -> List[str]:
    """
    Split text into chunks dengan overlap untuk preserve context

    Args:
        text: Text to split
        chunk_size: Maximum characters per chunk
        overlap: Characters to overlap between chunks

    Returns:
        List of text chunks
    """
```

**Mengapa Perlu Overlap?**

```
Tanpa Overlap:
  Chunk 1: "Python is a high-level programming"
  Chunk 2: "language. It supports multiple paradigms"
           ↑ Context lost! What "language"?

Dengan Overlap (200 chars):
  Chunk 1: "Python is a high-level programming"
  Chunk 2: "programming language. It supports multiple paradigms"
           ↑ Context preserved! Know it's about programming language
```

**Smart Boundary Detection:**

```python
# Try to split at sentence boundary
# Priority: . ! ? > word boundary > character

if '. ' in chunk or '! ' in chunk or '? ' in chunk:
    # Split at sentence
    split_at = max(
        chunk.rfind('. '),
        chunk.rfind('! '),
        chunk.rfind('? ')
    )
elif ' ' in chunk:
    # Split at word
    split_at = chunk.rfind(' ')
else:
    # Split at character (last resort)
    split_at = chunk_size
```

**Example:**

```python
text = """Python is a programming language. It is easy to learn.
Python has many libraries. NumPy is for numerical computing."""

chunks = split_text_with_overlap(text, chunk_size=50, overlap=20)

# Result:
# Chunk 1: "Python is a programming language."  (35 chars)
# Chunk 2: "language. It is easy to learn."     (overlap + new)
# Chunk 3: "learn. Python has many libraries."  (overlap + new)
# Chunk 4: "libraries. NumPy is for numerical computing."
```

**Function 2: create_chunk_id()**

```python
def create_chunk_id(document: str, page: int, chunk_index: int) -> str:
    """
    Create unique hierarchical ID for chunk

    Format: document.pdf::page_5::chunk_2
    """
    return f"{document}::page_{page}::chunk_{chunk_index}"
```

**Why Hierarchical ID?**
```
Benefits:
1. Unique across all documents
2. Easy to identify source
3. Easy to delete all chunks from one document
   (filter by document name)
4. Human-readable for debugging
```

**Function 3: get_file_hash()**

```python
def get_file_hash(file_path: Path) -> str:
    """
    Calculate MD5 hash of file for change detection

    Returns:
        MD5 hash string (32 chars)
    """
    import hashlib

    md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        # Read in chunks to handle large files
        for chunk in iter(lambda: f.read(4096), b''):
            md5.update(chunk)

    return md5.hexdigest()
```

**Use Case:**
```
Scenario: User modifies PDF

1. Get current hash: hash_new = get_file_hash(pdf_path)
2. Compare dengan stored hash: hash_old
3. If different → file changed → re-index
4. If same → no change → skip
```

**Function 4: format_source_citation()**

```python
def format_source_citation(metadata: dict) -> str:
    """
    Format metadata into citation string

    Args:
        metadata: {document: "doc.pdf", page: 5}

    Returns:
        "doc.pdf (Halaman 5)"
    """
    doc = metadata.get('document', 'Unknown')
    page = metadata.get('page', 'Unknown')
    return f"{doc} (Halaman {page})"
```

**Exercise:**

1. Implement `get_text_preview(text, max_length=100)`
   - Return first max_length characters + "..."
2. Implement `clean_filename(filename)`
   - Remove special characters
   - Replace spaces with underscores
3. Test your functions dengan pytest

### 3.3. PDFProcessor (src/pdf_processor.py)

**Purpose:** Extract text dari PDF dan chunk into pieces

**Pipeline:**

```
PDF File
  ↓ extract_text_from_pdf()
Pages Data (List of dicts)
  ↓ chunk_pages()
Chunks (List of dicts with metadata)
  ↓ (output)
Ready for embedding!
```

**Method 1: extract_text_from_pdf()**

```python
def extract_text_from_pdf(self, pdf_path: Path) -> List[Dict]:
    """
    Extract text page by page

    Returns:
        [
            {page_number: 1, text: "...", document: "file.pdf"},
            {page_number: 2, text: "...", document: "file.pdf"},
            ...
        ]
    """
    import pypdf

    pages_data = []

    with open(pdf_path, 'rb') as file:
        pdf_reader = pypdf.PdfReader(file)

        for page_num, page in enumerate(pdf_reader.pages, start=1):
            # Extract text
            text = page.extract_text()

            # Clean text
            text = self._clean_text(text)

            # Skip empty pages
            if not text.strip():
                continue

            pages_data.append({
                'page_number': page_num,
                'text': text,
                'document': pdf_path.name
            })

    return pages_data
```

**Why Page-by-Page?**
```
Keuntungan:
1. Memory efficient (don't load entire PDF at once)
2. Preserve page numbers (untuk citations)
3. Can skip empty pages
4. Can handle large PDFs (1000+ pages)
```

**Text Cleaning:**
```python
def _clean_text(self, text: str) -> str:
    """Remove artifacts dari PDF extraction"""

    # Remove null characters
    text = text.replace('\x00', '')

    # Normalize whitespace
    text = ' '.join(text.split())

    return text
```

**Common PDF Artifacts:**
- `\x00` (null characters)
- Multiple spaces/newlines
- Weird Unicode characters
- Hyphenation at line breaks

**Method 2: chunk_pages()**

```python
def chunk_pages(self, pages_data: List[Dict]) -> List[Dict]:
    """
    Split pages into chunks dengan metadata

    Input: Pages data
    Output: Chunks dengan unique IDs dan metadata
    """
    all_chunks = []

    for page_data in pages_data:
        page_num = page_data['page_number']
        text = page_data['text']
        document = page_data['document']

        # Split into chunks
        chunks_text = split_text_with_overlap(
            text,
            chunk_size=self.chunk_size,
            overlap=self.chunk_overlap
        )

        # Add metadata
        for idx, chunk_text in enumerate(chunks_text):
            chunk_id = create_chunk_id(document, page_num, idx)

            chunk = {
                'id': chunk_id,
                'text': chunk_text,
                'metadata': {
                    'document': document,
                    'page': page_num,
                    'chunk_index': idx,
                    'total_chunks_on_page': len(chunks_text)
                }
            }

            all_chunks.append(chunk)

    return all_chunks
```

**Metadata Purpose:**
```
metadata = {
    'document': "python.pdf",           # Which file?
    'page': 45,                         # Which page?
    'chunk_index': 2,                   # Which chunk on this page?
    'total_chunks_on_page': 5          # How many chunks total on page?
}

Uses:
- Citations: "python.pdf (Halaman 45)"
- Filtering: Only search in specific document
- Context: Know if chunk is start/middle/end of page
```

**Method 3: process_pdf() (Main Pipeline)**

```python
def process_pdf(self, pdf_path: Path) -> Dict:
    """
    Complete pipeline: extract → chunk → return summary
    """
    # Step 1: Extract
    pages_data = self.extract_text_from_pdf(pdf_path)

    # Step 2: Chunk
    chunks = self.chunk_pages(pages_data)

    # Step 3: Calculate hash
    file_hash = get_file_hash(pdf_path)

    # Step 4: Return summary
    return {
        'document': pdf_path.name,
        'file_hash': file_hash,
        'num_pages': len(pages_data),
        'num_chunks': len(chunks),
        'chunks': chunks
    }
```

**Exercise:**

Create test PDF dan process:
```python
processor = PDFProcessor(chunk_size=100, chunk_overlap=20)
result = processor.process_pdf(Path("test.pdf"))

print(f"Processed: {result['document']}")
print(f"Pages: {result['num_pages']}")
print(f"Chunks: {result['num_chunks']}")
print(f"First chunk: {result['chunks'][0]['text'][:50]}...")
```

### 3.4. EmbeddingGenerator (src/embeddings.py)

**Purpose:** Generate vector embeddings from text

**Model:** all-mpnet-base-v2 (sentence-transformers)

**Initialization:**

```python
from sentence_transformers import SentenceTransformer
import torch

class EmbeddingGenerator:
    def __init__(self, model_name=None, device=None):
        self.model_name = model_name or Config.EMBEDDING_MODEL
        self.device = device or Config.EMBEDDING_DEVICE

        # Auto-detect GPU
        if self.device == 'auto':
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'

        # Load model (first time: downloads ~420MB)
        self.model = SentenceTransformer(self.model_name, device=self.device)

        logger.info(f"Loaded {self.model_name} on {self.device}")
        logger.info(f"Embedding dimension: {self.model.get_sentence_embedding_dimension()}")
```

**GPU vs CPU:**
```
Performance (1000 texts):

CPU (Intel i7):
  ⏱️ Time: ~60 seconds
  💾 RAM: ~2GB

GPU (NVIDIA RTX 3060):
  ⏱️ Time: ~3 seconds  (20x faster!)
  💾 VRAM: ~1GB

Recommendation: Use GPU jika available!
```

**Method 1: generate_embedding() (Single Text)**

```python
def generate_embedding(self, text: str) -> List[float]:
    """
    Generate embedding untuk single text

    Args:
        text: Input text

    Returns:
        768-dimensional embedding vector
    """
    # Encode text
    embedding = self.model.encode(text, convert_to_numpy=True)

    # Convert numpy array to Python list
    return embedding.tolist()

# Example:
text = "Python is a programming language"
embedding = generator.generate_embedding(text)
# Result: [0.234, -0.567, ..., 0.891]  (768 floats)
```

**Internal Process:**

```
Text: "Python is a programming language"
  ↓
1. TOKENIZATION
   ["[CLS]", "Python", "is", "a", "programming", "language", "[SEP]"]
   (Special tokens: CLS=start, SEP=end)
  ↓
2. EMBEDDING LOOKUP
   Each token → initial embedding (768-dim)
  ↓
3. TRANSFORMER LAYERS (12 layers)
   - Self-attention (words attend to each other)
   - Feed-forward networks
   - Residual connections
   - Layer normalization
  ↓
4. MEAN POOLING
   Average all token embeddings
  ↓
5. L2 NORMALIZATION
   Normalize to unit length (||v|| = 1)
  ↓
Output: [0.234, -0.567, ..., 0.891]  (768 floats)
```

**Method 2: generate_embeddings_batch() (Multiple Texts)**

```python
def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings untuk multiple texts (more efficient!)

    Args:
        texts: List of input texts

    Returns:
        List of embeddings
    """
    embeddings = self.model.encode(
        texts,
        batch_size=32,           # Process 32 at a time
        show_progress_bar=True,  # Show progress
        convert_to_numpy=True
    )

    # Convert to list of lists
    return [emb.tolist() for emb in embeddings]

# Example:
texts = ["text 1", "text 2", ..., "text 100"]
embeddings = generator.generate_embeddings_batch(texts)
# Result: [[0.1, 0.2, ...], [0.3, 0.4, ...], ...]
#         ↑ 100 embeddings
```

**Why Batch Processing?**
```
Single Processing:
  for text in texts:
      embedding = model.encode(text)
  Time: n * t seconds

Batch Processing:
  embeddings = model.encode(texts, batch_size=32)
  Time: (n/32) * t seconds

Speedup: ~20-30x faster!
Reason: GPU processes multiple in parallel
```

**Method 3: embed_chunks() (Wrapper)**

```python
def embed_chunks(self, chunks: List[Dict]) -> List[Dict]:
    """
    Add embeddings to chunks

    Input:  [{'text': "...", 'metadata': {...}}]
    Output: [{'text': "...", 'metadata': {...}, 'embedding': [...]}]
    """
    # Extract texts
    texts = [chunk['text'] for chunk in chunks]

    # Generate embeddings batch
    embeddings = self.generate_embeddings_batch(texts)

    # Add to chunks
    for chunk, embedding in zip(chunks, embeddings):
        chunk['embedding'] = embedding

    return chunks
```

**Exercise:**

```python
# 1. Load model
generator = EmbeddingGenerator()

# 2. Generate single embedding
emb = generator.generate_embedding("Hello world")
print(f"Dimension: {len(emb)}")  # Should be 768

# 3. Generate batch
texts = ["Python is great", "I love coding", "Machine learning is fun"]
embs = generator.generate_embeddings_batch(texts)
print(f"Generated {len(embs)} embeddings")

# 4. Calculate similarity
from numpy import dot
from numpy.linalg import norm

def cosine_similarity(a, b):
    return dot(a, b) / (norm(a) * norm(b))

sim = cosine_similarity(embs[0], embs[1])
print(f"Similarity: {sim}")  # 0-1 (higher = more similar)
```

---

*[Materi dilanjutkan dengan modul berikutnya...]*

---

## 🔧 MODUL 4: Teknologi Deep Dive

### 4.1. FastMCP Framework

**Apa itu MCP?**

MCP = Model Context Protocol
- Standard untuk komunikasi antara LLMs dan tools
- Developed by Anthropic (Claude)
- Open protocol (bisa digunakan siapa saja)

**MCP Components:**

```
1. TOOLS
   Functions yang bisa dipanggil LLM
   Example: search_documents, send_email, get_weather

2. RESOURCES
   Data yang bisa diakses LLM
   Example: files, databases, APIs

3. PROMPTS
   Pre-defined prompts untuk LLM
   Example: "Summarize this document"
```

**FastMCP vs MCP SDK:**

```python
# MCP SDK (Low-level, verbose)
from mcp.server import Server, Tool
from mcp.types import TextContent

server = Server("my-server")

@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="query",
            description="Search docs",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"}
                }
            }
        )
    ]

@server.call_tool()
async def call_tool(name, arguments):
    if name == "query":
        result = do_search(arguments["query"])
        return [TextContent(type="text", text=result)]

# ~50 lines of boilerplate!
```

```python
# FastMCP (High-level, clean)
from fastmcp import FastMCP

mcp = FastMCP("my-server")

@mcp.tool()
def query(query: str) -> str:
    """Search docs"""
    return do_search(query)

# ~5 lines total!
```

**FastMCP Benefits:**
- ✅ 90% less boilerplate
- ✅ Auto schema from type hints
- ✅ Decorator-based (Pythonic)
- ✅ Built-in validation

**Exercise:**

Create simple MCP server:
```python
from fastmcp import FastMCP

mcp = FastMCP("calculator")

@mcp.tool()
def add(a: int, b: int) -> str:
    """Add two numbers"""
    return f"{a} + {b} = {a + b}"

@mcp.tool()
def multiply(a: int, b: int) -> str:
    """Multiply two numbers"""
    return f"{a} × {b} = {a * b}"

if __name__ == "__main__":
    mcp.run()
```

### 4.2. ChromaDB Vector Database

**Core Concepts:**

**1. Collections**
```python
# Like tables in SQL
collection = client.create_collection(
    name="documents",
    metadata={"hnsw:space": "cosine"}  # Similarity metric
)
```

**2. Storage Format**
```python
collection.add(
    ids=["id1", "id2"],                    # Unique identifiers
    documents=["text1", "text2"],          # Original text
    embeddings=[[0.1, 0.2, ...], [...]],  # 768-dim vectors
    metadatas=[{...}, {...}]              # Extra info
)
```

**3. Querying**
```python
results = collection.query(
    query_embeddings=[[0.1, 0.2, ...]],  # Query vector
    n_results=5,                          # Top 5
    where={"document": "python.pdf"}      # Filter (optional)
)
```

**Similarity Metrics:**

```
1. COSINE SIMILARITY (Default)
   Range: -1 to 1 (higher = more similar)
   Use: Text, semantic search
   Formula: cos(θ) = A·B / (||A|| ||B||)

2. L2 (Euclidean) DISTANCE
   Range: 0 to ∞ (lower = more similar)
   Use: When magnitude matters
   Formula: √(Σ(ai - bi)²)

3. INNER PRODUCT
   Range: -∞ to ∞ (higher = more similar)
   Use: When vectors normalized
   Formula: A·B
```

**HNSW Index:**

```
Hierarchical Navigable Small World Graph

Layer 3: [●]────[●]────[●]  (Coarse, few nodes)
           ↓      ↓      ↓
Layer 2: [●]─[●]─[●]─[●]─[●]  (Medium)
           ↓   ↓   ↓   ↓   ↓
Layer 1: [●][●][●][●][●][●][●]  (Fine, all nodes)

Search:
1. Start at top layer (coarse)
2. Navigate to closest node
3. Go down one layer
4. Repeat until bottom
5. Refine search at bottom layer

Time Complexity: O(log n) instead of O(n)
Trade-off: ~99% accuracy, 100x faster
```

**Exercise:**

```python
import chromadb

# 1. Create client
client = chromadb.Client()

# 2. Create collection
collection = client.create_collection("test")

# 3. Add data
collection.add(
    ids=["1", "2", "3"],
    documents=["Python is great", "I love coding", "Dogs are cute"],
    metadatas=[{"lang": "en"}, {"lang": "en"}, {"lang": "en"}]
)

# 4. Query
results = collection.query(
    query_texts=["Programming languages"],  # ChromaDB auto-embeds!
    n_results=2
)

print(results)
```

---

## 📝 MODUL 5: Best Practices & Tips

### 5.1. Chunking Strategy

**Optimal Chunk Size:**

```
Too Small (< 200 chars):
  ❌ Lost context
  ❌ Too many chunks
  ❌ Higher cost

Optimal (500-1000 chars):
  ✅ Good context
  ✅ Reasonable count
  ✅ Good quality

Too Large (> 2000 chars):
  ❌ Multiple topics混在
  ❌ Less precise
  ❌ Worse retrieval
```

**Recommendations:**

```
Document Type    | Chunk Size | Overlap
─────────────────|────────────|─────────
Academic papers  | 800-1000   | 200
Technical docs   | 600-800    | 150
Books           | 1000-1500  | 250
Code docs       | 400-600    | 100
```

### 5.2. Embedding Best Practices

**1. Batch Processing**
```python
# ❌ DON'T: Process one by one
for text in texts:
    emb = model.encode(text)  # Slow!

# ✅ DO: Batch process
embs = model.encode(texts, batch_size=32)  # Fast!
```

**2. GPU Utilization**
```python
# Check GPU available
import torch
if torch.cuda.is_available():
    device = 'cuda'
    print(f"Using GPU: {torch.cuda.get_device_name(0)}")
else:
    device = 'cpu'

model = SentenceTransformer(model_name, device=device)
```

**3. Memory Management**
```python
# For very large datasets
for i in range(0, len(texts), 1000):
    batch = texts[i:i+1000]
    embeddings = model.encode(batch)
    store_in_database(embeddings)
    # Process in chunks of 1000
```

### 5.3. Query Optimization

**1. Appropriate top_k**
```
Use Case        | Recommended top_k
────────────────|──────────────────
Quick answer    | 3-5
Comprehensive   | 10-15
Research        | 20-30
```

**2. Metadata Filtering**
```python
# Search only in specific document
results = vector_store.query(
    query_embedding=emb,
    filter_dict={"document": "python.pdf"}
)

# Search only recent pages
results = vector_store.query(
    query_embedding=emb,
    filter_dict={"page": {"$gte": 100}}  # page >= 100
)
```

**3. Re-ranking**
```python
# First pass: Get top 20
results = vector_store.query(emb, top_k=20)

# Second pass: Re-rank by custom logic
re_ranked = sorted(
    results,
    key=lambda x: custom_score(x),
    reverse=True
)[:5]  # Get top 5 after re-ranking
```

### 5.4. Performance Tips

**1. Indexing**
```bash
# Estimate time:
# CPU: ~30-60 seconds per 100 pages
# GPU: ~3-5 seconds per 100 pages

# For 1000-page book:
# CPU: ~5-10 minutes
# GPU: ~30-50 seconds
```

**2. Query Latency**
```
Component           | Time
────────────────────|────────
Embedding query     | ~50ms (GPU) / ~200ms (CPU)
Vector search       | ~10-50ms (depends on DB size)
Result formatting   | ~5ms
────────────────────|────────
Total               | ~65-255ms
```

**3. Optimization Techniques**
```python
# 1. Connection pooling
# 2. Caching embeddings
# 3. Async processing
# 4. Load balancing
```

### 5.5. Common Pitfalls

**1. Embedding Model Mismatch**
```python
# ❌ DON'T: Change models mid-way
# Embeddings not compatible!

# ✅ DO: Stick to one model
# Or re-index everything if changing
```

**2. Forgetting to Clean Text**
```python
# ❌ DON'T: Index raw PDF text
raw_text = page.extract_text()  # Has artifacts!

# ✅ DO: Clean first
clean_text = clean_text(raw_text)
```

**3. No Error Handling**
```python
# ❌ DON'T: Assume success
result = process_pdf(path)

# ✅ DO: Handle errors
try:
    result = process_pdf(path)
except Exception as e:
    logger.error(f"Failed: {e}")
    # Retry or alert
```

### 5.6. Quiz Modul 5

**Pertanyaan:**

1. Apa chunk size optimal untuk technical documentation?
2. Kapan sebaiknya menggunakan GPU untuk embeddings?
3. Sebutkan 3 cara optimize query performance
4. Apa yang terjadi jika kita ganti embedding model?
5. Mengapa perlu batch processing untuk embeddings?

---

## 📖 GLOSSARY

**Istilah Teknis dalam Bahasa Indonesia:**

| English Term | Bahasa Indonesia | Penjelasan |
|--------------|------------------|------------|
| Embedding | Penyematan / Vektor Makna | Representasi text dalam bentuk angka |
| Chunk | Potongan Text | Bagian kecil dari dokumen |
| Vector | Vektor | Array angka yang merepresentasikan data |
| Similarity | Kemiripan | Seberapa mirip dua vektor |
| Semantic | Semantik / Makna | Berhubungan dengan makna, bukan kata |
| Retrieval | Pengambilan | Proses mencari informasi |
| Augmentation | Penambahan / Penguat | Menambah informasi tambahan |
| Generation | Pembangkitan | Proses membuat output |
| Index | Indeks | Struktur data untuk search cepat |
| Query | Kueri / Pertanyaan | Pencarian atau pertanyaan |
| Pipeline | Jalur Proses | Serangkaian tahapan proses |
| Orchestration | Orkestrasi | Mengkoordinasi berbagai komponen |
| Debouncing | Pembatasan Event | Menunggu sebelum proses event |
| Metadata | Metadata | Data tentang data |
| Latency | Latensi | Waktu tunggu / delay |
| Throughput | Laju Proses | Jumlah proses per satuan waktu |
| Batch | Kelompok | Proses banyak item sekaligus |

---

## 🎯 LEARNING PATH

**Untuk Pemula:**
1. Start dengan Modul 1 (Concepts)
2. Hands-on Lab 1 & 2
3. Modul 2 (Architecture)
4. Hands-on Lab 3
5. Modul 3 (Components)
6. Hands-on Lab 4 & 5

**Untuk Advanced:**
1. Quick review Modul 1 & 2
2. Deep dive Modul 3 & 4
3. Modul 5 (Best Practices)
4. Challenge Projects

---

## 📚 REFERENSI

**Official Docs:**
- FastMCP: https://github.com/jlowin/fastmcp
- ChromaDB: https://docs.trychroma.com/
- Sentence-Transformers: https://www.sbert.net/
- PyPDF: https://pypdf2.readthedocs.io/

**Learning Resources:**
- Vector Databases: https://www.pinecone.io/learn/vector-database/
- RAG Systems: https://www.anthropic.com/index/retrieval-augmented-generation
- Embeddings: https://platform.openai.com/docs/guides/embeddings

**Videos (Recommended):**
- "What are Vector Embeddings?" - 3Blue1Brown
- "RAG Explained" - AI Explained
- "Vector Databases 101" - ByteByteGo

---

Semoga materi pengajaran ini membantu! 🚀
