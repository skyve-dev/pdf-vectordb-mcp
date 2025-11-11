# Data Flow: Proses Query/Search

## Overview
Dokumen ini menjelaskan aliran data lengkap saat user melakukan search/query terhadap indexed PDFs.

## High-Level Flow

```
┌─────────┐      ┌──────────┐      ┌───────────┐      ┌──────────┐      ┌──────────┐
│  User   │─────▶│   MCP    │─────▶│ Embedding │─────▶│  Vector  │─────▶│ ChromaDB │
│ Claude  │      │  Server  │      │ Generator │      │  Store   │      │          │
└─────────┘      └──────────┘      └───────────┘      └──────────┘      └──────────┘
    ▲                                                         │                │
    │                                                         ▼                │
    │                                                   Similarity         HNSW
    │                                                     Search           Index
    │                                                         │                │
    │                                                         ▼                ▼
    └────────────────────────────────────────────── Results ◀────────────────┘
```

## Detailed Step-by-Step Flow

### Step 1: User Query via Claude Desktop

```
┌────────────────────────────────────────────┐
│          Claude Desktop                    │
│                                            │
│  User bertanya:                            │
│  "What are the key findings in the         │
│   executive summary?"                      │
│                                            │
│  MCP Client mengirim request:              │
│  {                                         │
│    "tool": "search_pdfs",                  │
│    "params": {                             │
│      "query": "key findings executive     │
│                 summary",                  │
│      "top_k": 5                            │
│    }                                       │
│  }                                         │
└────────────────────────────────────────────┘
              │
              │ STDIO Communication
              │ (JSON-RPC over stdin/stdout)
              ▼
┌────────────────────────────────────────────┐
│        MCP Server (mcp_server.py)          │
│                                            │
│  @mcp.tool()                               │
│  async def search_pdfs(                    │
│      query: str,                           │
│      top_k: int = 5                        │
│  ):                                        │
│      # Receive query                       │
└────────────────────────────────────────────┘
```

### Step 2: Query Validation & Preprocessing

```
┌────────────────────────────────────────────────────────────┐
│              MCP Server: search_pdfs()                     │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  Input:                                                    │
│  • query = "key findings executive summary"               │
│  • top_k = 5                                               │
│                                                            │
│  2.1 Validate query                                        │
│  ┌──────────────────────────────────────────────────┐    │
│  │  if not query or len(query.strip()) == 0:        │    │
│  │      return error: "Query cannot be empty"       │    │
│  │                                                   │    │
│  │  if top_k < 1 or top_k > 100:                    │    │
│  │      return error: "Invalid top_k value"         │    │
│  └──────────────────────────────────────────────────┘    │
│                                                            │
│  2.2 Clean query (optional)                               │
│  ┌──────────────────────────────────────────────────┐    │
│  │  query = query.strip()                           │    │
│  │  # Remove extra whitespace                       │    │
│  │  # Normalize case (model handles this internally)│    │
│  └──────────────────────────────────────────────────┘    │
│                                                            │
│  Validated query: "key findings executive summary" ✓      │
│                                                            │
└────────────────────────────────────────────────────────────┘
              │
              │ Valid query
              ▼
```

### Step 3: Generate Query Embedding

```
┌────────────────────────────────────────────────────────────┐
│      EmbeddingGenerator: generate(query)                   │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  Input: "key findings executive summary"                   │
│                                                            │
│  3.1 Model already loaded (from indexing)                 │
│  ┌──────────────────────────────────────────────────┐    │
│  │  # Model in memory: all-mpnet-base-v2            │    │
│  │  # No need to reload - reuse same model          │    │
│  └──────────────────────────────────────────────────┘    │
│                                                            │
│  3.2 Encode query → vector                                │
│  ┌──────────────────────────────────────────────────┐    │
│  │  query_embedding = self.model.encode(            │    │
│  │      "key findings executive summary",           │    │
│  │      show_progress_bar=False                     │    │
│  │  )                                                │    │
│  │                                                   │    │
│  │  # Fast encoding (~50ms for 1 query on CPU)      │    │
│  └──────────────────────────────────────────────────┘    │
│                                                            │
│  Output: Query embedding vector                           │
│  ┌──────────────────────────────────────────────────┐    │
│  │  query_embedding = [                             │    │
│  │      0.0456,                                      │    │
│  │     -0.0234,                                      │    │
│  │      0.0789,                                      │    │
│  │      ...                                          │    │
│  │     -0.0123                                       │    │
│  │  ]                                                │    │
│  │  # Shape: (768,) - same dimensionality as docs   │    │
│  └──────────────────────────────────────────────────┘    │
│                                                            │
│  Why same model as indexing?                              │
│  • CRITICAL: Query & documents MUST use same model        │
│  • Different models → incompatible vector spaces          │
│  • Similarity comparison would be meaningless             │
│                                                            │
└────────────────────────────────────────────────────────────┘
              │
              │ Query embedding (768-dim vector)
              ▼
```

### Step 4: Vector Similarity Search

```
┌────────────────────────────────────────────────────────────┐
│         VectorStore: search()                              │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  Input:                                                    │
│  • query_embedding = [0.0456, -0.0234, ...]               │
│  • top_k = 5                                               │
│                                                            │
│  4.1 Query ChromaDB collection                            │
│  ┌──────────────────────────────────────────────────┐    │
│  │  results = self.collection.query(                │    │
│  │      query_embeddings=[query_embedding],         │    │
│  │      n_results=top_k,                            │    │
│  │      include=['documents', 'metadatas',          │    │
│  │               'distances']                       │    │
│  │  )                                                │    │
│  │                                                   │    │
│  │  # ChromaDB internally:                          │    │
│  │  # 1. Uses HNSW index for fast ANN search       │    │
│  │  # 2. Computes cosine similarity                │    │
│  │  # 3. Returns top-k most similar chunks          │    │
│  └──────────────────────────────────────────────────┘    │
│                                                            │
└────────────────────────────────────────────────────────────┘
              │
              │ Raw results from ChromaDB
              ▼
```

### Step 4.5: How HNSW Index Works (Internal)

```
┌────────────────────────────────────────────────────────────┐
│           ChromaDB: HNSW Index Search                      │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  HNSW = Hierarchical Navigable Small World Graph          │
│                                                            │
│  Visualization:                                            │
│                                                            │
│  Layer 2 (Top):     ○───────○                            │
│                     │╲     ╱│                             │
│  Layer 1 (Middle):  ○─○───○─○                            │
│                     │╲│╲ ╱│╱│                             │
│  Layer 0 (Base):    ○─○─○─○─○─○─○─○ ... (all vectors)   │
│                                                            │
│  Search Process:                                           │
│  1. Start at top layer with entry point                   │
│  2. Navigate to closest neighbor at this layer            │
│  3. Drop down to next layer, continue navigating          │
│  4. Reach bottom layer, find exact k-nearest neighbors    │
│                                                            │
│  Time Complexity:                                          │
│  • Brute force: O(N) - compare with ALL vectors           │
│  • HNSW: O(log N) - navigate through graph layers         │
│                                                            │
│  Example with 10,000 documents:                           │
│  • Brute force: 10,000 comparisons                        │
│  • HNSW: ~14 comparisons (log₂ 10000 ≈ 13.3)            │
│                                                            │
│  Similarity Metric: Cosine Similarity                     │
│  ┌──────────────────────────────────────────────────┐    │
│  │  similarity = dot(query_vec, doc_vec) /          │    │
│  │               (norm(query_vec) * norm(doc_vec))  │    │
│  │                                                   │    │
│  │  Range: [-1, 1]                                   │    │
│  │    1.0  = identical vectors                       │    │
│  │    0.0  = orthogonal (no similarity)             │    │
│  │   -1.0  = opposite vectors                        │    │
│  │                                                   │    │
│  │  ChromaDB returns distance = 1 - similarity       │    │
│  │  So: distance ∈ [0, 2]                           │    │
│  │      0.0 = most similar                           │    │
│  │      2.0 = most dissimilar                        │    │
│  └──────────────────────────────────────────────────┘    │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### Step 5: Process Search Results

```
┌────────────────────────────────────────────────────────────┐
│         VectorStore: Format results                        │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  Raw ChromaDB output:                                      │
│  ┌──────────────────────────────────────────────────┐    │
│  │  {                                                │    │
│  │    "ids": [["report_2024_chunk_0",               │    │
│  │             "report_2024_chunk_15", ...]],       │    │
│  │    "documents": [["Executive Summary text...",   │    │
│  │                   "Analysis section text...", ]]│    │
│  │    "metadatas": [[{                              │    │
│  │        "file_path": "pdfs/report_2024.pdf",     │    │
│  │        "chunk_index": 0,                         │    │
│  │        ...                                        │    │
│  │    }, ...]],                                      │    │
│  │    "distances": [[0.234, 0.456, 0.567, ...]]    │    │
│  │  }                                                │    │
│  └──────────────────────────────────────────────────┘    │
│                                                            │
│  Format into list of result objects:                      │
│  ┌──────────────────────────────────────────────────┐    │
│  │  formatted_results = []                          │    │
│  │                                                   │    │
│  │  for i in range(len(results['ids'][0])):        │    │
│  │      result = {                                   │    │
│  │          "chunk_id": results['ids'][0][i],       │    │
│  │          "text": results['documents'][0][i],     │    │
│  │          "metadata": results['metadatas'][0][i], │    │
│  │          "distance": results['distances'][0][i], │    │
│  │          "similarity": 1 - distance               │    │
│  │      }                                            │    │
│  │      formatted_results.append(result)            │    │
│  └──────────────────────────────────────────────────┘    │
│                                                            │
│  Output: List of 5 results (top_k=5)                      │
│                                                            │
└────────────────────────────────────────────────────────────┘
              │
              │ Formatted results
              ▼
```

### Step 6: Rank & Return Results

```
┌────────────────────────────────────────────────────────────┐
│         MCP Server: Prepare response                       │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  Results (sorted by similarity, highest first):            │
│                                                            │
│  Result 1: ⭐⭐⭐⭐⭐ (Most relevant)                      │
│  ┌──────────────────────────────────────────────────┐    │
│  │  {                                                │    │
│  │    "chunk_id": "report_2024_chunk_0",            │    │
│  │    "text": "Executive Summary\n\nKey Findings:   │    │
│  │             Our analysis revealed three main     │    │
│  │             insights: 1) Market growth of 23%... │    │
│  │             [truncated for display]",            │    │
│  │    "file_path": "pdfs/report_2024.pdf",         │    │
│  │    "file_name": "report_2024.pdf",               │    │
│  │    "chunk_index": 0,                             │    │
│  │    "similarity": 0.876,  ← 87.6% similar         │    │
│  │    "distance": 0.124                             │    │
│  │  }                                                │    │
│  └──────────────────────────────────────────────────┘    │
│                                                            │
│  Result 2: ⭐⭐⭐⭐                                        │
│  ┌──────────────────────────────────────────────────┐    │
│  │  {                                                │    │
│  │    "chunk_id": "report_2024_chunk_15",           │    │
│  │    "text": "Summary of Key Points\n\nIn this    │    │
│  │             section, we summarize the findings...│    │
│  │             [truncated]",                         │    │
│  │    "file_path": "pdfs/report_2024.pdf",         │    │
│  │    "similarity": 0.743,  ← 74.3% similar         │    │
│  │    "distance": 0.257                             │    │
│  │  }                                                │    │
│  └──────────────────────────────────────────────────┘    │
│                                                            │
│  Result 3: ⭐⭐⭐                                          │
│  ┌──────────────────────────────────────────────────┐    │
│  │  {                                                │    │
│  │    "chunk_id": "analysis_2024_chunk_8",          │    │
│  │    "text": "Analysis Results\n\nOur executive   │    │
│  │             team reviewed the quarterly data...  │    │
│  │             [truncated]",                         │    │
│  │    "file_path": "pdfs/analysis_2024.pdf",       │    │
│  │    "similarity": 0.689,  ← 68.9% similar         │    │
│  │    "distance": 0.311                             │    │
│  │  }                                                │    │
│  └──────────────────────────────────────────────────┘    │
│                                                            │
│  Result 4: ⭐⭐                                            │
│  • similarity: 0.654                                      │
│                                                            │
│  Result 5: ⭐                                              │
│  • similarity: 0.612                                      │
│                                                            │
└────────────────────────────────────────────────────────────┘
              │
              │ Top 5 results
              ▼
```

### Step 7: Send to Claude Desktop

```
┌────────────────────────────────────────────────────────────┐
│         MCP Server: Return via MCP Protocol                │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  Prepare MCP response:                                     │
│  ┌──────────────────────────────────────────────────┐    │
│  │  response = {                                     │    │
│  │      "results": [                                 │    │
│  │          {result1}, {result2}, ... {result5}     │    │
│  │      ],                                            │    │
│  │      "total_results": 5,                          │    │
│  │      "query": "key findings executive summary"    │    │
│  │  }                                                │    │
│  │                                                   │    │
│  │  return response                                  │    │
│  └──────────────────────────────────────────────────┘    │
│                                                            │
└────────────────────────────────────────────────────────────┘
              │
              │ MCP Protocol (JSON-RPC)
              ▼
┌────────────────────────────────────────────────────────────┐
│              Claude Desktop                                │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  Claude receives results and can:                         │
│  1. Read the relevant text chunks                         │
│  2. Synthesize an answer based on retrieved context       │
│  3. Present formatted response to user                    │
│                                                            │
│  Example Claude response:                                  │
│  ┌──────────────────────────────────────────────────┐    │
│  │  Based on your documents, here are the key       │    │
│  │  findings from the executive summary:            │    │
│  │                                                   │    │
│  │  1. **Market Growth**: The analysis revealed     │    │
│  │     a 23% growth in the target market over       │    │
│  │     the past quarter.                             │    │
│  │                                                   │    │
│  │  2. **Revenue Increase**: Quarterly revenue      │    │
│  │     exceeded projections by 15%.                 │    │
│  │                                                   │    │
│  │  3. **Customer Satisfaction**: Customer NPS      │    │
│  │     scores improved from 45 to 62.               │    │
│  │                                                   │    │
│  │  Source: report_2024.pdf (Executive Summary)     │    │
│  └──────────────────────────────────────────────────┘    │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

## Comparison: Semantic vs Keyword Search

### Semantic Search (Our Implementation)

```
Query: "key findings executive summary"

Vector Representation:
query_embedding = [0.0456, -0.0234, 0.0789, ...]

Matches documents with SIMILAR MEANING:
✅ "Executive Summary - Key Points"      (similarity: 0.876)
✅ "Summary of Main Findings"             (similarity: 0.743)
✅ "Critical Results Overview"            (similarity: 0.689)
✅ "Important Discoveries - Synopsis"     (similarity: 0.654)

Even if exact words don't match!
```

### Traditional Keyword Search

```
Query: "key findings executive summary"

Exact word matching:
✅ "executive summary" appears → Match
❌ "critical results overview" → No match (even if same meaning!)
❌ "main discoveries synopsis" → No match

Misses semantically similar content!
```

## Timeline & Performance

```
Step 1: Receive Query                  ⚡ < 1ms
   ↓
Step 2: Validate                       ⚡ < 1ms
   ↓
Step 3: Generate Query Embedding       ⚡ ~50ms (CPU)
   ↓                                      ⚡ ~10ms (GPU)
Step 4: Vector Search (HNSW)           ⚡ ~20ms (10k docs)
   ↓                                      ⚡ ~50ms (100k docs)
Step 5: Format Results                 ⚡ ~5ms
   ↓
Step 6-7: Return to User               ⚡ < 1ms
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total: ~80ms (typical query on CPU)
       ~40ms (with GPU acceleration)
```

**Why so fast?**
- HNSW index: O(log N) instead of O(N)
- No need to recompute document embeddings (already stored!)
- Only compute 1 query embedding
- Efficient similarity computation in ChromaDB

## Scaling Example

### Database with 100 PDFs (10,000 chunks)

```
Brute Force Approach:
• Compare query with ALL 10,000 embeddings
• Time: 10,000 × 0.01ms = 100ms (best case)

HNSW Index Approach:
• Navigate graph: ~log₂(10000) ≈ 14 comparisons
• Time: 14 × 0.01ms = 0.14ms (best case)
• Actual: ~20ms (including overhead)

Speed-up: 5x faster!
```

### Database with 1,000 PDFs (100,000 chunks)

```
Brute Force Approach:
• Time: 100,000 × 0.01ms = 1000ms = 1 second

HNSW Index Approach:
• Navigate: ~log₂(100000) ≈ 17 comparisons
• Time: ~50ms

Speed-up: 20x faster!
```

## Result Quality Factors

### 1. Embedding Quality
```
Good Model (all-mpnet-base-v2):
✅ Trained on diverse text
✅ 768 dimensions = rich representation
✅ Captures semantic nuances

Poor Model:
❌ Small dimensions (e.g., 50-dim)
❌ Limited training data
❌ Poor semantic understanding
```

### 2. Chunk Size
```
Too Small (e.g., 200 chars):
❌ Not enough context
❌ Incomplete sentences
❌ Poor semantic representation

Optimal (1000 chars):
✅ Complete paragraphs
✅ Sufficient context
✅ Good semantic unit

Too Large (e.g., 5000 chars):
❌ Mixed topics in one chunk
❌ Diluted relevance
❌ Less precise retrieval
```

### 3. Top-K Selection
```
Too Few (k=1):
❌ Might miss relevant info
❌ No diversity in results

Optimal (k=3-10):
✅ Multiple perspectives
✅ Good coverage
✅ Manageable for LLM to process

Too Many (k=50):
❌ Information overload
❌ Diluted relevance
❌ Slower processing
```

## Error Handling

```
┌─────────────────────────────────────────────┐
│  Possible Errors & Handling                 │
├─────────────────────────────────────────────┤
│                                             │
│  1. Empty query                             │
│     → Return error: "Query cannot be empty" │
│                                             │
│  2. Invalid top_k                           │
│     → Return error: "Invalid top_k value"   │
│                                             │
│  3. No documents in database                │
│     → Return: {results: [], total: 0}       │
│                                             │
│  4. Embedding generation failed             │
│     → Return error: "Failed to embed query" │
│                                             │
│  5. ChromaDB query failed                   │
│     → Return error: "Search failed"         │
│                                             │
│  6. No relevant results (all low similarity)│
│     → Return results with low scores        │
│     → Let Claude decide if useful           │
│                                             │
└─────────────────────────────────────────────┘
```

## Summary

Proses query melibatkan 7 langkah:
1. **Receive** - Terima query dari user
2. **Validate** - Validasi query & parameters
3. **Embed** - Generate query embedding (768-dim vector)
4. **Search** - HNSW index search untuk similar chunks
5. **Format** - Format hasil dengan metadata
6. **Rank** - Sort by similarity score
7. **Return** - Return top-k results ke Claude

Total waktu: **~80ms** per query (sangat cepat!)

**Key Advantages:**
- Semantic understanding (meaning, not just keywords)
- Fast retrieval (HNSW index)
- Scalable (log N complexity)
- Quality results (relevant chunks with metadata)

