# LATIHAN PRAKTIKUM: PDF VECTOR DB MCP SERVER

**Format:** Step-by-step hands-on labs
**Target:** Learn by doing
**Durasi:** 1-2 jam per lab

---

## 🧪 LAB 1: Setup & Instalasi

**Tujuan:**
- Install semua dependencies
- Verify installation
- Understand project structure

**Prerequisites:**
- Python 3.8+ installed
- Git installed
- Text editor (VS Code recommended)

### Step 1: Clone/Download Project

```bash
# If using git:
git clone <repository-url>
cd pdf-vectordb-mcp

# Or download ZIP dan extract
```

### Step 2: Create Virtual Environment

```bash
# Windows:
python -m venv venv
venv\Scripts\activate

# Mac/Linux:
python3 -m venv venv
source venv/bin/activate
```

**Verification:**
```bash
# Should show (venv) in prompt
# Example: (venv) C:\pdf-vectordb-mcp>
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**What's being installed?**
```
fastmcp           → MCP framework
chromadb          → Vector database
sentence-transformers → Embedding model
torch             → ML framework (~2GB!)
pypdf             → PDF processing
pdfplumber        → Alternative PDF processor
watchdog          → File monitoring
python-dotenv     → Environment variables
```

**Expected Duration:**
- With good internet: 5-10 minutes
- Torch is large (~2GB), be patient!

### Step 4: Verify Installation

Create file `test_installation.py`:

```python
"""
Test semua dependencies installed correctly
"""

def test_imports():
    """Test import all major libraries"""
    try:
        print("Testing imports...")

        print("✓ fastmcp...", end=" ")
        from fastmcp import FastMCP
        print("OK")

        print("✓ chromadb...", end=" ")
        import chromadb
        print("OK")

        print("✓ sentence-transformers...", end=" ")
        from sentence_transformers import SentenceTransformer
        print("OK")

        print("✓ torch...", end=" ")
        import torch
        print(f"OK (CUDA available: {torch.cuda.is_available()})")

        print("✓ pypdf...", end=" ")
        import pypdf
        print("OK")

        print("✓ watchdog...", end=" ")
        from watchdog.observers import Observer
        print("OK")

        print("\n✅ All imports successful!")
        return True

    except ImportError as e:
        print(f"\n❌ Import failed: {e}")
        return False

def test_model_loading():
    """Test loading embedding model"""
    print("\nTesting model loading...")
    print("(This will download ~420MB on first run)")

    try:
        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer('all-mpnet-base-v2')
        print("✅ Model loaded successfully!")

        # Test embedding generation
        embedding = model.encode("test")
        print(f"✅ Embedding generated: {len(embedding)} dimensions")

        return True

    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        return False

if __name__ == "__main__":
    # Test 1: Imports
    if not test_imports():
        print("\n❌ Fix import errors before continuing!")
        exit(1)

    # Test 2: Model
    if not test_model_loading():
        print("\n❌ Fix model loading before continuing!")
        exit(1)

    print("\n🎉 All tests passed! Ready to continue.")
```

Run test:
```bash
python test_installation.py
```

**Expected Output:**
```
Testing imports...
✓ fastmcp... OK
✓ chromadb... OK
✓ sentence-transformers... OK
✓ torch... OK (CUDA available: False)
✓ pypdf... OK
✓ watchdog... OK

✅ All imports successful!

Testing model loading...
(This will download ~420MB on first run)
Downloading model...
✅ Model loaded successfully!
✅ Embedding generated: 768 dimensions

🎉 All tests passed! Ready to continue.
```

### Step 5: Explore Project Structure

```bash
# List all files
ls -R  # Mac/Linux
dir /s  # Windows

# Or use tree command if available
tree
```

**Task:** Identify these directories:
- [ ] src/ (source code)
- [ ] data/ (where PDFs go)
- [ ] tests/ (unit tests)

**Task:** Identify these files:
- [ ] src/mcp_server.py (main server)
- [ ] src/config.py (configuration)
- [ ] .env.example (config template)
- [ ] requirements.txt (dependencies)

### Step 6: Configuration

```bash
# Copy .env.example to .env
cp .env.example .env  # Mac/Linux
copy .env.example .env  # Windows

# Open .env in editor
code .env  # VS Code
# or
notepad .env  # Windows
# or
nano .env  # Linux
```

**Default Configuration:**
```bash
# Embedding (Local, no API key needed!)
EMBEDDING_MODEL=all-mpnet-base-v2
EMBEDDING_DEVICE=auto  # auto, cpu, or cuda

# Paths
PDF_FOLDER=./data/pdfs
CHROMA_DB_PATH=./data/chroma_db

# Chunking
CHUNK_SIZE=800
CHUNK_OVERLAP=200

# Retrieval
DEFAULT_TOP_K=5

# Logging
LOG_LEVEL=INFO
```

**No changes needed** untuk default setup!

### Lab 1 Checkpoint

**✅ You should now have:**
- [x] Virtual environment activated
- [x] All dependencies installed
- [x] Imports working
- [x] Model downloaded
- [x] Project structure understood
- [x] Configuration file ready

**Troubleshooting:**

**Problem:** "pip install fails"
```bash
# Solution: Upgrade pip
python -m pip install --upgrade pip
```

**Problem:** "torch too large to download"
```bash
# Solution: Install CPU-only version (smaller)
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

**Problem:** "Model download timeout"
```bash
# Solution: Try again, or download manually
# Check: https://huggingface.co/sentence-transformers/all-mpnet-base-v2
```

---

## 📄 LAB 2: First PDF Indexing

**Tujuan:**
- Prepare sample PDF
- Index first PDF
- Understand indexing process

### Step 1: Prepare Test PDF

**Option A: Use Existing PDF**
```bash
# Copy any PDF to data/pdfs/
cp ~/Documents/sample.pdf data/pdfs/
```

**Option B: Download Sample**
```bash
# Download free Python tutorial PDF
# (Or any educational PDF dari internet)
```

**Option C: Create Simple PDF**
```python
"""
Create simple test PDF
"""
from reportlab.pdfgen import canvas

def create_test_pdf(filename):
    c = canvas.Canvas(filename)

    # Page 1
    c.drawString(100, 750, "Python Programming Basics")
    c.drawString(100, 700, "")
    c.drawString(100, 680, "Chapter 1: Introduction")
    c.drawString(100, 660, "Python is a high-level programming language.")
    c.drawString(100, 640, "It is known for its simplicity and readability.")
    c.showPage()

    # Page 2
    c.drawString(100, 750, "Chapter 2: Functions")
    c.drawString(100, 700, "")
    c.drawString(100, 680, "Functions are defined using the def keyword.")
    c.drawString(100, 660, "Example: def hello(): print('Hello')")
    c.showPage()

    c.save()
    print(f"Created {filename}")

if __name__ == "__main__":
    create_test_pdf("data/pdfs/python-basics.pdf")
```

**Verify PDF exists:**
```bash
ls data/pdfs/
# Should show your PDF file
```

### Step 2: Manual Indexing (Interactive)

Create `manual_index.py`:

```python
"""
Manually index a PDF to understand the process
"""
from pathlib import Path
from src.pdf_processor import PDFProcessor
from src.embeddings import EmbeddingGenerator
from src.vector_store import VectorStore

def index_pdf_step_by_step(pdf_path: Path):
    """Index PDF dengan detailed output"""

    print(f"📄 Processing: {pdf_path.name}")
    print("="*60)

    # Step 1: Initialize components
    print("\n1️⃣ Initializing components...")
    pdf_processor = PDFProcessor()
    embedding_generator = EmbeddingGenerator()
    vector_store = VectorStore()
    print("✅ Components initialized")

    # Step 2: Extract text
    print("\n2️⃣ Extracting text from PDF...")
    result = pdf_processor.process_pdf(pdf_path)
    print(f"✅ Extracted {result['num_pages']} pages")
    print(f"✅ Created {result['num_chunks']} chunks")

    # Show first chunk
    first_chunk = result['chunks'][0]
    print(f"\nFirst chunk preview:")
    print(f"  ID: {first_chunk['id']}")
    print(f"  Text: {first_chunk['text'][:100]}...")
    print(f"  Metadata: {first_chunk['metadata']}")

    # Step 3: Generate embeddings
    print("\n3️⃣ Generating embeddings...")
    chunks_with_embeddings = embedding_generator.embed_chunks(result['chunks'])
    print(f"✅ Generated {len(chunks_with_embeddings)} embeddings")

    # Show embedding info
    first_embedding = chunks_with_embeddings[0]['embedding']
    print(f"\nEmbedding info:")
    print(f"  Dimensions: {len(first_embedding)}")
    print(f"  First 5 values: {first_embedding[:5]}")
    print(f"  Range: [{min(first_embedding):.3f}, {max(first_embedding):.3f}]")

    # Step 4: Store in database
    print("\n4️⃣ Storing in vector database...")
    embeddings = [chunk['embedding'] for chunk in chunks_with_embeddings]
    vector_store.add_chunks(result['chunks'], embeddings)
    print("✅ Stored in ChromaDB")

    # Step 5: Verify
    print("\n5️⃣ Verifying indexing...")
    docs = vector_store.list_documents()
    print(f"✅ Total documents in database: {len(docs)}")
    for doc in docs:
        print(f"   - {doc['document']}: {doc['num_chunks']} chunks")

    print("\n🎉 Indexing complete!")
    print("="*60)

if __name__ == "__main__":
    # Index the PDF
    pdf_path = Path("data/pdfs/python-basics.pdf")

    if not pdf_path.exists():
        print(f"❌ PDF not found: {pdf_path}")
        print("Create/copy a PDF to data/pdfs/ first!")
        exit(1)

    index_pdf_step_by_step(pdf_path)
```

Run:
```bash
python manual_index.py
```

**Expected Output:**
```
📄 Processing: python-basics.pdf
============================================================

1️⃣ Initializing components...
✅ Components initialized

2️⃣ Extracting text from PDF...
✅ Extracted 2 pages
✅ Created 3 chunks

First chunk preview:
  ID: python-basics.pdf::page_1::chunk_0
  Text: Python Programming Basics  Chapter 1: Introduction Python is a high-level programming language...
  Metadata: {'document': 'python-basics.pdf', 'page': 1, 'chunk_index': 0}

3️⃣ Generating embeddings...
Batches: 100%|████████| 1/1 [00:00<00:00,  6.71it/s]
✅ Generated 3 embeddings

Embedding info:
  Dimensions: 768
  First 5 values: [0.234, -0.567, 0.123, 0.891, -0.234]
  Range: [-0.892, 0.945]

4️⃣ Storing in vector database...
✅ Stored in ChromaDB

5️⃣ Verifying indexing...
✅ Total documents in database: 1
   - python-basics.pdf: 3 chunks

🎉 Indexing complete!
============================================================
```

### Step 3: Inspect Database

```python
"""
Inspect what's in ChromaDB
"""
from src.vector_store import VectorStore

def inspect_database():
    store = VectorStore()

    # Get all documents
    docs = store.list_documents()

    print("📊 Database Contents")
    print("="*60)
    print(f"Total documents: {len(docs)}\n")

    for doc in docs:
        print(f"Document: {doc['document']}")
        print(f"  Pages: {doc['num_pages']}")
        print(f"  Chunks: {doc['num_chunks']}")
        print()

    # Get stats
    stats = store.get_stats()
    print(f"Total chunks in database: {stats['total_chunks']}")

if __name__ == "__main__":
    inspect_database()
```

### Step 4: First Query (Without MCP)

```python
"""
Query the indexed PDF directly (without Claude/MCP)
"""
from src.embeddings import EmbeddingGenerator
from src.vector_store import VectorStore
from src.utils import format_source_citation

def query_database(query_text: str, top_k: int = 3):
    """Simple query function"""

    print(f"🔍 Query: {query_text}")
    print("="*60)

    # Initialize
    embedding_generator = EmbeddingGenerator()
    vector_store = VectorStore()

    # Generate query embedding
    print("\n1️⃣ Generating query embedding...")
    query_embedding = embedding_generator.generate_embedding(query_text)
    print("✅ Query embedded")

    # Search
    print(f"\n2️⃣ Searching for top {top_k} results...")
    results = vector_store.query(query_embedding, top_k=top_k)
    print(f"✅ Found {len(results['documents'][0])} results")

    # Display results
    print("\n📑 Results:")
    print("="*60)

    for idx, (doc, metadata, distance) in enumerate(zip(
        results['documents'][0],
        results['metadatas'][0],
        results['distances'][0]
    ), start=1):
        similarity = (1 - distance) * 100
        source = format_source_citation(metadata)

        print(f"\n--- Result {idx} ---")
        print(f"Source: {source}")
        print(f"Relevance: {similarity:.1f}%")
        print(f"\n{doc}\n")

if __name__ == "__main__":
    # Try different queries
    queries = [
        "What is Python?",
        "How to define functions?",
        "Programming language features"
    ]

    for query in queries:
        query_database(query, top_k=2)
        print("\n" + "="*60 + "\n")
```

### Lab 2 Checkpoint

**✅ You should now have:**
- [x] Sample PDF in data/pdfs/
- [x] PDF indexed successfully
- [x] Understand extraction process
- [x] Understand embedding generation
- [x] Understand storage in ChromaDB
- [x] Can query directly

**Questions to Answer:**

1. How many chunks were created from your PDF?
2. What is the embedding dimension?
3. What metadata is stored with each chunk?
4. Can you find relevant information with queries?

**Experiments:**

1. **Try different chunk sizes:**
   ```python
   processor = PDFProcessor(chunk_size=500, chunk_overlap=100)
   processor = PDFProcessor(chunk_size=1500, chunk_overlap=300)
   # How does it affect number of chunks?
   ```

2. **Measure indexing time:**
   ```python
   import time
   start = time.time()
   # ... indexing code ...
   end = time.time()
   print(f"Time taken: {end - start:.2f} seconds")
   ```

3. **Compare with different queries:**
   - Exact match query
   - Semantic similar query
   - Completely different query

---

## 🔍 LAB 3: Query & Search Experiments

**Tujuan:**
- Understand semantic search
- Compare different query styles
- Analyze relevance scores

### Step 1: Create Test Corpus

Add multiple PDFs dengan different topics:
```
data/pdfs/
  ├── python-basics.pdf (programming)
  ├── cooking-recipes.pdf (food)
  └── history-notes.pdf (history)
```

Index all:
```bash
python manual_index.py data/pdfs/python-basics.pdf
python manual_index.py data/pdfs/cooking-recipes.pdf
python manual_index.py data/pdfs/history-notes.pdf
```

### Step 2: Semantic Search Demo

```python
"""
Demonstrate semantic search capabilities
"""
from src.embeddings import EmbeddingGenerator
from src.vector_store import VectorStore

def semantic_search_demo():
    """Show that semantic search finds meaning, not keywords"""

    generator = EmbeddingGenerator()
    store = VectorStore()

    # Test cases: Query → Expected topic
    test_cases = [
        ("coding in Python", "programming"),
        ("making pasta", "food"),
        ("World War 2", "history"),
        ("functions and loops", "programming"),
        ("ingredients for cake", "food")
    ]

    print("🔬 Semantic Search Demonstration")
    print("="*60)

    for query, expected_topic in test_cases:
        print(f"\nQuery: '{query}'")
        print(f"Expected topic: {expected_topic}")

        # Search
        query_emb = generator.generate_embedding(query)
        results = store.query(query_emb, top_k=1)

        # Get top result
        top_doc = results['metadatas'][0][0]['document']
        similarity = (1 - results['distances'][0][0]) * 100

        print(f"Top result: {top_doc} ({similarity:.1f}% relevant)")

        # Check if correct
        is_correct = expected_topic in top_doc.lower()
        print(f"{'✅ Correct!' if is_correct else '❌ Wrong'}")

if __name__ == "__main__":
    semantic_search_demo()
```

### Step 3: Query Variations

```python
"""
Test how query phrasing affects results
"""

def test_query_variations(base_concept: str):
    """Test different ways to ask the same thing"""

    generator = EmbeddingGenerator()
    store = VectorStore()

    # Different phrasings of same concept
    if base_concept == "functions":
        queries = [
            "How to define functions?",
            "Function definition in Python",
            "Creating reusable code blocks",
            "def keyword usage"
        ]
    elif base_concept == "loops":
        queries = [
            "How to loop in Python?",
            "Iterating through lists",
            "for and while statements",
            "Repeating code execution"
        ]

    print(f"Testing variations for concept: {base_concept}")
    print("="*60)

    for query in queries:
        print(f"\nQuery: '{query}'")

        # Search
        query_emb = generator.generate_embedding(query)
        results = store.query(query_emb, top_k=1)

        # Show top result
        top_text = results['documents'][0][0][:100]
        similarity = (1 - results['distances'][0][0]) * 100

        print(f"Top result ({similarity:.1f}%): {top_text}...")

if __name__ == "__main__":
    test_query_variations("functions")
    print("\n" + "="*60 + "\n")
    test_query_variations("loops")
```

### Step 4: Relevance Analysis

```python
"""
Analyze relevance scores distribution
"""
import matplotlib.pyplot as plt
import numpy as np

def analyze_relevance_scores(query: str, top_k: int = 20):
    """Plot relevance scores untuk visual analysis"""

    generator = EmbeddingGenerator()
    store = VectorStore()

    # Search
    query_emb = generator.generate_embedding(query)
    results = store.query(query_emb, top_k=top_k)

    # Calculate similarities
    similarities = [(1 - d) * 100 for d in results['distances'][0]]

    # Print statistics
    print(f"Query: '{query}'")
    print("="*60)
    print(f"Top result: {similarities[0]:.1f}%")
    print(f"Average: {np.mean(similarities):.1f}%")
    print(f"Median: {np.median(similarities):.1f}%")
    print(f"Std dev: {np.std(similarities):.1f}%")

    # Plot
    plt.figure(figsize=(10, 6))
    plt.bar(range(1, top_k+1), similarities)
    plt.xlabel('Result Rank')
    plt.ylabel('Relevance Score (%)')
    plt.title(f'Relevance Scores: "{query}"')
    plt.axhline(y=50, color='r', linestyle='--', label='50% threshold')
    plt.legend()
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(f'relevance_analysis.png')
    print(f"\n📊 Plot saved to: relevance_analysis.png")

if __name__ == "__main__":
    analyze_relevance_scores("Python programming language features")
```

### Lab 3 Checkpoint

**✅ You should now understand:**
- [x] Semantic search vs keyword search
- [x] How query phrasing affects results
- [x] Relevance score interpretation
- [x] How to analyze search quality

**Experiments:**

1. **Find Query Threshold:**
   - At what similarity % are results still useful?
   - Try different top_k values (3, 5, 10, 20)

2. **Cross-Topic Queries:**
   - Query about programming, get cooking results?
   - How low is the relevance score?

3. **Multilingual (if applicable):**
   - Try queries in different languages
   - Does the model understand?

---

## ⚙️ LAB 4: Configuration & Tuning

**Tujuan:**
- Understand configuration impact
- Tune for your use case
- Optimize performance

### Step 1: Chunk Size Experiments

```python
"""
Test impact of different chunk sizes
"""
from pathlib import Path
from src.pdf_processor import PDFProcessor
import time

def test_chunk_sizes(pdf_path: Path):
    """Test different chunk configurations"""

    configs = [
        (400, 100),   # Small chunks, small overlap
        (800, 200),   # Medium (default)
        (1500, 300),  # Large chunks
        (800, 50),    # Same size, less overlap
        (800, 400),   # Same size, large overlap
    ]

    print("🔬 Chunk Size Experiment")
    print("="*60)

    for chunk_size, overlap in configs:
        print(f"\nConfig: size={chunk_size}, overlap={overlap}")

        # Process
        start = time.time()
        processor = PDFProcessor(chunk_size=chunk_size, chunk_overlap=overlap)
        result = processor.process_pdf(pdf_path)
        end = time.time()

        # Stats
        num_chunks = result['num_chunks']
        time_taken = end - start

        print(f"  Chunks created: {num_chunks}")
        print(f"  Time taken: {time_taken:.2f}s")
        print(f"  Avg chunk length: {sum(len(c['text']) for c in result['chunks']) / num_chunks:.0f} chars")

if __name__ == "__main__":
    pdf_path = Path("data/pdfs/python-basics.pdf")
    test_chunk_sizes(pdf_path)
```

**Analysis Questions:**
- Which config creates most chunks?
- Which is fastest?
- What's the trade-off?

### Step 2: Device Performance (CPU vs GPU)

```python
"""
Compare CPU vs GPU performance
"""
import torch
import time
from src.embeddings import EmbeddingGenerator

def benchmark_devices():
    """Benchmark embedding generation on different devices"""

    # Sample texts
    texts = [f"Sample text number {i}" for i in range(100)]

    devices = ['cpu']
    if torch.cuda.is_available():
        devices.append('cuda')

    print("⚡ Device Performance Benchmark")
    print("="*60)

    for device in devices:
        print(f"\n🖥️  Device: {device.upper()}")

        # Initialize generator
        generator = EmbeddingGenerator(device=device)

        # Benchmark
        start = time.time()
        embeddings = generator.generate_embeddings_batch(texts)
        end = time.time()

        time_taken = end - start
        texts_per_sec = len(texts) / time_taken

        print(f"  Time: {time_taken:.2f}s")
        print(f"  Speed: {texts_per_sec:.1f} texts/sec")

        if device == 'cpu':
            cpu_time = time_taken

    # Comparison
    if len(devices) > 1:
        speedup = cpu_time / time_taken
        print(f"\n🚀 GPU Speedup: {speedup:.1f}x faster!")

if __name__ == "__main__":
    benchmark_devices()
```

### Step 3: Top-K Tuning

```python
"""
Find optimal top_k for your use case
"""

def tune_top_k(query: str):
    """Test different top_k values"""

    from src.embeddings import EmbeddingGenerator
    from src.vector_store import VectorStore

    generator = EmbeddingGenerator()
    store = VectorStore()

    # Test different top_k
    top_k_values = [1, 3, 5, 10, 20]

    print(f"Query: '{query}'")
    print("="*60)

    query_emb = generator.generate_embedding(query)

    for k in top_k_values:
        results = store.query(query_emb, top_k=k)

        # Calculate stats
        similarities = [(1 - d) * 100 for d in results['distances'][0]]
        avg_sim = sum(similarities) / len(similarities)
        min_sim = min(similarities)

        print(f"\ntop_k={k}:")
        print(f"  Best: {similarities[0]:.1f}%")
        print(f"  Average: {avg_sim:.1f}%")
        print(f"  Worst: {min_sim:.1f}%")
        print(f"  Range: {similarities[0] - min_sim:.1f}%")

if __name__ == "__main__":
    tune_top_k("Python programming basics")
```

**Decision Guide:**
```
Use Case           | Recommended top_k
───────────────────|──────────────────
Quick answer       | 3-5
Comprehensive info | 10-15
Research/explore   | 20-30
```

### Step 4: Memory Profiling

```python
"""
Monitor memory usage during indexing
"""
import psutil
import os

def profile_memory(pdf_path: Path):
    """Profile memory usage"""

    from src.pdf_processor import PDFProcessor
    from src.embeddings import EmbeddingGenerator
    from src.vector_store import VectorStore

    process = psutil.Process(os.getpid())

    def get_memory_mb():
        return process.memory_info().rss / 1024 / 1024

    print("💾 Memory Profiling")
    print("="*60)

    # Baseline
    mem_start = get_memory_mb()
    print(f"\nBaseline: {mem_start:.1f} MB")

    # Extract
    processor = PDFProcessor()
    result = processor.process_pdf(pdf_path)
    mem_after_extract = get_memory_mb()
    print(f"After extraction: {mem_after_extract:.1f} MB (+{mem_after_extract - mem_start:.1f} MB)")

    # Embed
    generator = EmbeddingGenerator()
    chunks = generator.embed_chunks(result['chunks'])
    mem_after_embed = get_memory_mb()
    print(f"After embedding: {mem_after_embed:.1f} MB (+{mem_after_embed - mem_after_extract:.1f} MB)")

    # Store
    store = VectorStore()
    embeddings = [c['embedding'] for c in chunks]
    store.add_chunks(result['chunks'], embeddings)
    mem_after_store = get_memory_mb()
    print(f"After storage: {mem_after_store:.1f} MB (+{mem_after_store - mem_after_embed:.1f} MB)")

    # Total
    print(f"\nTotal memory increase: {mem_after_store - mem_start:.1f} MB")

if __name__ == "__main__":
    pdf_path = Path("data/pdfs/python-basics.pdf")
    profile_memory(pdf_path)
```

### Lab 4 Checkpoint

**✅ You should now know:**
- [x] Impact of chunk size on results
- [x] CPU vs GPU performance difference
- [x] Optimal top_k for different use cases
- [x] Memory requirements

**Optimization Recommendations:**

Document your optimal config:
```
# My optimal config for [use case]:
CHUNK_SIZE=[your value]
CHUNK_OVERLAP=[your value]
DEFAULT_TOP_K=[your value]
EMBEDDING_DEVICE=[cpu or cuda]
```

---

## 🔄 LAB 5: Real-Time Indexing & File Watching

**Tujuan:**
- Understand file watching
- Test auto-indexing
- Handle file modifications

### Step 1: Start Server with File Watching

```bash
# Start the full server
python run_server.py
```

**Expected Output:**
```
Initializing PDF Vector DB MCP Server...
INFO - Successfully loaded model: all-mpnet-base-v2
INFO - Embedding dimension: 768
INFO - Indexed 3 existing PDFs
INFO - Started watching directory: ./data/pdfs
INFO - MCP server running on stdio
```

### Step 2: Test Auto-Indexing

**In another terminal (keep server running):**

```bash
# Copy new PDF
cp ~/Downloads/new-document.pdf data/pdfs/

# Watch server logs for:
# "PDF created: new-document.pdf"
# "Processing PDF: new-document.pdf"
# "Successfully indexed X chunks"
```

**Observation Questions:**
- How long after copying does indexing start?
- Does it block other operations?
- What happens if copy is slow (large file)?

### Step 3: Test File Modification

```python
"""
Modify existing PDF and observe re-indexing
"""
import time
from pathlib import Path
import shutil

def test_modification():
    """Test PDF modification detection"""

    original = Path("data/pdfs/python-basics.pdf")
    backup = Path("data/pdfs/python-basics-backup.pdf")

    print("Testing file modification detection")
    print("="*60)

    # Backup original
    shutil.copy(original, backup)
    print("✅ Created backup")

    # Wait for server to process
    time.sleep(3)

    # "Modify" by updating timestamp
    original.touch()
    print("✅ Updated file timestamp")
    print("⏳ Server should detect modification...")

    # Wait for processing
    time.sleep(5)

    # Restore backup
    shutil.move(backup, original)
    print("✅ Restored original")

if __name__ == "__main__":
    test_modification()
```

### Step 4: Test Deletion

```bash
# Delete a PDF
rm data/pdfs/old-document.pdf

# Watch server logs for:
# "PDF deleted: old-document.pdf"
# "Removing from database: old-document.pdf"
```

### Step 5: Stress Test

```python
"""
Add multiple PDFs rapidly
"""
import time
from pathlib import Path
import shutil

def stress_test():
    """Add multiple files quickly"""

    source = Path("data/pdfs/python-basics.pdf")

    print("Stress Test: Adding 5 PDFs rapidly")
    print("="*60)

    for i in range(5):
        dest = Path(f"data/pdfs/test-copy-{i}.pdf")
        shutil.copy(source, dest)
        print(f"✅ Added: {dest.name}")
        time.sleep(0.5)  # Small delay

    print("\n⏳ Server should process all files...")
    print("Watch server logs!")

    # Wait
    time.sleep(30)

    print("\n🧹 Cleaning up...")
    for i in range(5):
        dest = Path(f"data/pdfs/test-copy-{i}.pdf")
        if dest.exists():
            dest.unlink()
    print("✅ Cleanup done")

if __name__ == "__main__":
    stress_test()
```

### Lab 5 Checkpoint

**✅ You should now understand:**
- [x] How file watching works
- [x] Auto-indexing process
- [x] Handling modifications
- [x] Debouncing behavior

**Advanced Experiments:**

1. **Test debouncing:**
   - Copy large file (100MB+)
   - Does it wait for complete copy?

2. **Concurrent operations:**
   - Add file while querying
   - Does query work during indexing?

3. **Error recovery:**
   - Add corrupt PDF
   - Does server crash or handle gracefully?

---

## 🚀 LAB 6: Integration with Claude Desktop

**Tujuan:**
- Connect server to Claude Desktop
- Test MCP tools
- End-to-end workflow

### Step 1: Configure Claude Desktop

Edit Claude Desktop config:
```bash
# Windows:
notepad %APPDATA%\Claude\claude_desktop_config.json

# Mac:
code ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

Add configuration:
```json
{
  "mcpServers": {
    "pdf-vectordb": {
      "command": "python",
      "args": ["-m", "src.mcp_server"],
      "cwd": "C:\\full\\path\\to\\pdf-vectordb-mcp"
    }
  }
}
```

**⚠️ Important:** Replace with YOUR actual path!

### Step 2: Restart Claude Desktop

1. Completely close Claude Desktop
2. Reopen Claude Desktop
3. Wait 15-20 seconds (model loading)
4. Check if server appears in settings

### Step 3: Test Tools in Claude

**Test 1: List Documents**
```
You: "What documents do you have access to?"

Expected: Claude uses list_documents() tool
Response shows your indexed PDFs
```

**Test 2: Simple Query**
```
You: "What is Python?"

Expected: Claude uses query_documents() tool
Response cites your PDFs
```

**Test 3: Specific Document**
```
You: "Search for functions only in python-basics.pdf"

Expected: Claude uses query with document filter
Response only from that PDF
```

**Test 4: Get Stats**
```
You: "Show me system statistics"

Expected: Claude uses get_system_stats() tool
Response shows config and stats
```

### Step 4: End-to-End Workflow

**Scenario: Research Assistant**

```
1. You: "I just added a new PDF about machine learning"
   (Add ML PDF to data/pdfs/)

2. Wait for auto-indexing (watch logs)

3. You: "What documents do you now have?"
   Claude: Lists including new ML PDF

4. You: "What is supervised learning?"
   Claude: Searches, cites ML PDF, explains concept

5. You: "Compare this with information about Python"
   Claude: Searches both PDFs, compares concepts
```

### Step 5: Troubleshooting

**Problem:** Server not showing in Claude

Solutions checklist:
- [ ] Is Python path correct in config?
- [ ] Is project path absolute (not relative)?
- [ ] Did you restart Claude completely?
- [ ] Check Claude logs: `%APPDATA%\Claude\logs\main.log`

**Problem:** Tools slow to respond

Reasons:
- Large PDFs (embedding takes time)
- CPU vs GPU (GPU 20x faster)
- First query after startup (model loading)

**Problem:** Wrong results

Check:
- Is PDF properly indexed?
- Try different query phrasing
- Check relevance scores (may be too low)

### Lab 6 Checkpoint

**✅ You should now have:**
- [x] Server connected to Claude Desktop
- [x] Tools working correctly
- [x] End-to-end workflow tested
- [x] Troubleshooting experience

**Celebrate! 🎉**

You have a fully functional RAG system integrated with Claude!

---

## 🏆 CHALLENGE PROJECTS

**For Advanced Students:**

### Challenge 1: Multi-Language Support
- Add PDFs in different languages
- Test if embeddings work across languages
- Create multilingual search

### Challenge 2: Custom Metadata
- Add custom metadata (tags, categories, dates)
- Implement filtering by metadata
- Create category-based search

### Challenge 3: Performance Dashboard
- Create web dashboard showing:
  - Number of documents
  - Query statistics
  - Response times
  - Memory usage

### Challenge 4: Citation Generator
- Extract text dengan format citation
- Generate bibliography
- Export to BibTeX format

### Challenge 5: Hybrid Search
- Combine semantic search + keyword search
- Implement BM25 scoring
- Create hybrid ranking algorithm

### Challenge 6: Advanced Chunking
- Implement paragraph-based chunking
- Section-aware chunking
- Hierarchical chunking (document → section → paragraph)

---

## 📊 LAB REPORT TEMPLATE

```markdown
# Lab Report: [Lab Number & Name]

**Name:** [Your Name]
**Date:** [Date]
**Lab Duration:** [Time]

## Objectives
- [ ] Objective 1
- [ ] Objective 2
- [ ] Objective 3

## Setup
- Python version: [version]
- Operating System: [OS]
- GPU available: [Yes/No]

## Results

### Experiment 1: [Name]
**Procedure:**
1. Step 1
2. Step 2
3. Step 3

**Results:**
- Metric 1: [value]
- Metric 2: [value]

**Screenshots:**
[Insert screenshot]

**Observations:**
[Your observations]

### Experiment 2: [Name]
...

## Analysis
[Your analysis of results]

## Challenges Faced
1. Challenge 1 → Solution
2. Challenge 2 → Solution

## Conclusions
[What you learned]

## Questions
[Any questions for instructor]
```

---

## 🔗 ADDITIONAL RESOURCES

**Documentation:**
- [DOKUMENTASI_LENGKAP.md](./DOKUMENTASI_LENGKAP.md) - Full technical docs
- [MATERI_PENGAJARAN.md](./MATERI_PENGAJARAN.md) - Lecture materials
- [README.md](./README.md) - Quick start guide

**Online Resources:**
- Sentence-Transformers: https://www.sbert.net/
- ChromaDB Docs: https://docs.trychroma.com/
- FastMCP GitHub: https://github.com/jlowin/fastmcp

**Videos:**
- "Understanding Embeddings" - 3Blue1Brown
- "Vector Databases Explained" - Fireship
- "RAG Systems Tutorial" - AI Jason

---

Selamat belajar! Jangan ragu untuk bereksperimen dan explore! 🚀
