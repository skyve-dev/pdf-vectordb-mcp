# Diagram dan Visualisasi

Folder ini berisi diagram-diagram visual (ASCII art) yang menjelaskan berbagai aspek dari PDF Vector DB MCP Server.

## Daftar Diagram

### 1. [Arsitektur 3-Tier](01_arsitektur_3tier.md)
**Topik**: Arsitektur sistem secara keseluruhan

**Isi**:
- Diagram lengkap 3-tier layered architecture
- Presentation Layer (MCP Server)
- Business Logic Layer (Processors, Embeddings, Utils)
- Data Access Layer (VectorStore, ChromaDB)
- Cross-cutting concerns (Config)
- Dependency flow dan design patterns

**Cocok untuk**:
- Memahami struktur high-level aplikasi
- Belajar tentang separation of concerns
- Memahami dependency injection pattern
- Pengenalan design patterns yang digunakan

---

### 2. [Data Flow: Indexing](02_dataflow_indexing.md)
**Topik**: Aliran data saat indexing PDF

**Isi**:
- Step-by-step flow dari user input sampai storage
- Path resolution & validation
- PDF text extraction dengan PyPDF2
- Text chunking dengan overlap
- Embedding generation dengan SentenceTransformers
- Storage ke ChromaDB dengan HNSW index
- Timeline & performance metrics

**Cocok untuk**:
- Memahami bagaimana PDF diproses
- Belajar tentang chunking strategy
- Memahami embedding generation
- Troubleshooting indexing issues

---

### 3. [Data Flow: Query/Search](03_dataflow_query.md)
**Topik**: Aliran data saat search/query

**Isi**:
- Query validation & preprocessing
- Query embedding generation
- Vector similarity search dengan HNSW
- Cosine similarity computation
- Result ranking & formatting
- Semantic vs keyword search comparison
- Performance analysis

**Cocok untuk**:
- Memahami bagaimana search bekerja
- Belajar tentang vector similarity search
- Memahami HNSW index algorithm
- Optimasi query performance

---

### 4. [Component Interaction](04_component_interaction.md)
**Topik**: Interaksi antar komponen

**Isi**:
- Complete system component map
- Detailed interaction patterns
- MCP Server orchestration
- Config management
- PDFProcessor ↔ Utils
- EmbeddingGenerator ↔ ML Model (lazy loading)
- VectorStore ↔ ChromaDB (façade pattern)
- FileWatcher integration
- Sequence diagrams
- Dependency graph
- Communication patterns
- Error propagation
- Component lifecycle

**Cocok untuk**:
- Memahami bagaimana komponen saling berkomunikasi
- Belajar tentang design patterns (Façade, Observer, Lazy Loading)
- Debugging complex interactions
- Understanding dependency injection

---

### 5. [Chunking Strategy](05_chunking_strategy.md)
**Topik**: Strategi chunking text

**Isi**:
- Why chunking is needed
- Problem dengan full document embedding
- Core parameters (chunk_size, chunk_overlap)
- Algorithm visualization dengan overlap
- Why 200 characters overlap?
- Why 1000 characters chunk size?
- Real-world examples
- Search example dengan chunks
- Implementation code
- Optimization tips
- Smart boundary detection
- Metadata-aware chunking

**Cocok untuk**:
- Memahami mengapa chunking penting
- Belajar parameter tuning
- Optimasi retrieval quality
- Understanding trade-offs

---

## Urutan Pembelajaran yang Disarankan

### Untuk Pemula (Belum Familiar dengan RAG/Vector Search)

```
1. Chunking Strategy (05_chunking_strategy.md)
   └─ Mulai dari konsep dasar chunking
   └─ Pahami why & how

2. Data Flow: Indexing (02_dataflow_indexing.md)
   └─ Ikuti alur indexing step-by-step
   └─ Lihat bagaimana chunks dibuat dan di-embed

3. Data Flow: Query (03_dataflow_query.md)
   └─ Lihat bagaimana search bekerja
   └─ Pahami semantic search

4. Arsitektur 3-Tier (01_arsitektur_3tier.md)
   └─ Sekarang pahami big picture
   └─ Lihat bagaimana semua pieces fit together

5. Component Interaction (04_component_interaction.md)
   └─ Deep dive ke detail interactions
   └─ Pelajari design patterns
```

### Untuk Developer (Sudah Familiar dengan Konsep Dasar)

```
1. Arsitektur 3-Tier (01_arsitektur_3tier.md)
   └─ Start dengan high-level overview

2. Component Interaction (04_component_interaction.md)
   └─ Pahami detailed interactions
   └─ Study design patterns

3. Data Flow: Indexing (02_dataflow_indexing.md)
   └─ Detail implementation indexing

4. Data Flow: Query (03_dataflow_query.md)
   └─ Detail implementation query

5. Chunking Strategy (05_chunking_strategy.md)
   └─ Optimization & tuning
```

### Untuk Guru/Pengajar

```
Sesi 1: Pengenalan
└─ 01_arsitektur_3tier.md (Overview)
└─ 05_chunking_strategy.md (Konsep fundamental)

Sesi 2: Indexing Deep Dive
└─ 02_dataflow_indexing.md (Step-by-step)

Sesi 3: Search Deep Dive
└─ 03_dataflow_query.md (HNSW, similarity)

Sesi 4: Advanced Topics
└─ 04_component_interaction.md (Design patterns)
```

---

## Cara Menggunakan Diagram Ini

### 1. Untuk Belajar Sendiri
- Baca diagram sesuai urutan yang disarankan di atas
- Coba trace flow diagram sambil lihat source code
- Experiment dengan parameters (chunk_size, top_k, dll)

### 2. Untuk Teaching
- Gunakan diagram sebagai visual aids
- Print atau tampilkan di projector
- Walk through step-by-step dengan students
- Combine dengan hands-on labs dari LATIHAN_PRAKTIKUM.md

### 3. Untuk Debugging
- Lihat data flow diagram untuk understand execution path
- Check component interaction untuk verify dependencies
- Use as reference saat troubleshooting issues

### 4. Untuk Code Review
- Reference architecture diagram untuk verify design
- Check component interaction untuk validate patterns
- Ensure consistency dengan established patterns

---

## Notasi yang Digunakan

### Boxes/Containers
```
┌─────────────┐
│  Component  │  ← Box untuk represent komponen
└─────────────┘
```

### Arrows & Flow
```
│  ← Vertical flow
▼  ← Downward direction
▶  ← Rightward direction
─  ← Connection line
```

### Emphasis
```
✅ ← Good practice / Success
❌ ← Bad practice / Error
⚠️  ← Warning / Caution
🔥 ← Performance intensive
⚡ ← Fast operation
💾 ← Storage operation
📄 ← Document/File
```

### Code Blocks
````
```
Code or pseudocode
```
````

---

## Konvensi Diagram

1. **Top-to-Bottom Flow**: Execution flow dari atas ke bawah
2. **Left-to-Right Sequence**: Time sequence dari kiri ke kanan
3. **Indentation**: Menunjukkan hierarchy atau nested structure
4. **Color via ASCII**: Menggunakan box characters untuk grouping

---

## Feedback dan Update

Jika ada:
- Pertanyaan tentang diagram
- Request untuk diagram tambahan
- Kesalahan atau ketidakjelasan
- Saran improvement

Silakan update diagram atau buat issue untuk diskusi.

---

## Lihat Juga

- **[DOKUMENTASI_LENGKAP.md](../DOKUMENTASI_LENGKAP.md)** - Dokumentasi teknis detail
- **[MATERI_PENGAJARAN.md](../MATERI_PENGAJARAN.md)** - Materi terstruktur untuk mengajar
- **[LATIHAN_PRAKTIKUM.md](../LATIHAN_PRAKTIKUM.md)** - Hands-on lab exercises
- **Source code** di folder `src/` - Implementasi actual

---

## Tips Membaca Diagram ASCII

1. **Gunakan monospace font** (Courier, Monaco, Consolas)
   - Agar alignment box characters benar

2. **Zoom out jika perlu** untuk lihat big picture

3. **Print/Save as PDF** untuk referensi offline

4. **Trace dengan jari/kursor** saat follow flow diagram

5. **Baca keterangan** di setiap section untuk context

---

**Selamat belajar! 🚀**

Diagram-diagram ini dirancang untuk membantu Anda memahami PDF Vector DB MCP Server secara visual dan intuitif.

