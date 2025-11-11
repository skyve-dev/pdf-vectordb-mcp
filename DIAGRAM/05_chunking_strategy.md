# Chunking Strategy Illustration

## Overview
Dokumen ini menjelaskan strategi chunking yang digunakan untuk memecah teks PDF menjadi chunks yang optimal untuk vector search.

## Why Chunking?

### Problem: Full Document Embedding

```
┌─────────────────────────────────────────────────────────────┐
│                    Full 100-page PDF                        │
│                      (~150,000 chars)                       │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ Embed as one document?
                            ▼
                    ❌ PROBLEMS ❌

1. Information Dilution
   • Single embedding represents ALL topics
   • Specific information "lost" in the average
   • Poor retrieval precision

2. Relevance Issues
   • User asks: "What's the Q4 revenue?"
   • System retrieves: Entire 100-page document
   • User needs to read everything to find answer

3. Context Window Limits
   • LLMs have token limits (e.g., 200k tokens)
   • Can't process entire large documents efficiently
   • Need to extract only relevant sections

4. Processing Inefficiency
   • Slow embedding generation for huge text
   • Expensive vector operations
   • Difficult to cache and reuse
```

### Solution: Chunk into Smaller Pieces

```
┌─────────────────────────────────────────────────────────────┐
│                    Full 100-page PDF                        │
│                      (~150,000 chars)                       │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ Split into chunks
                            ▼
┌──────────┐  ┌──────────┐  ┌──────────┐       ┌──────────┐
│ Chunk 1  │  │ Chunk 2  │  │ Chunk 3  │  ...  │Chunk 188 │
│Executive │  │Intro &   │  │Methods & │       │Conclusion│
│Summary   │  │Background│  │Analysis  │       │          │
└──────────┘  └──────────┘  └──────────┘       └──────────┘
    │             │              │                    │
    │ Each chunk has its own embedding                │
    ▼             ▼              ▼                    ▼
[0.02, ...]  [0.05, ...]    [-0.01, ...]       [0.03, ...]

✅ BENEFITS ✅

1. Precision
   • Each chunk represents specific topic
   • Better semantic representation
   • More accurate retrieval

2. Relevance
   • Retrieve only relevant chunks
   • User gets exactly what they need
   • No information overload

3. Efficiency
   • Smaller embeddings = faster processing
   • Can cache individual chunks
   • Incremental updates possible
```

## Our Chunking Strategy

### Core Parameters

```
┌────────────────────────────────────────┐
│     Chunking Configuration             │
├────────────────────────────────────────┤
│                                        │
│  CHUNK_SIZE = 1000 characters          │
│  └─ Each chunk contains ~1000 chars    │
│                                        │
│  CHUNK_OVERLAP = 200 characters        │
│  └─ 200 chars overlap between chunks   │
│                                        │
└────────────────────────────────────────┘
```

### Algorithm Visualization

```
Input Text (3000 characters):
┌────────────────────────────────────────────────────────────────────┐
│ "Executive Summary: Our analysis of Q4 2024 shows significant...  │
│  ...growth in key metrics. Revenue increased by 23% compared to..│
│  ...previous quarter. Customer satisfaction improved from 45 to...│
│  ...62 based on NPS scores. Market share expanded in three main...│
│  ...regions. Detailed breakdown: Revenue streams showed strong... │
│  ...performance across all categories..." [continues...]          │
└────────────────────────────────────────────────────────────────────┘

Step-by-Step Chunking:

Step 1: Extract first chunk (0 → 1000)
┌────────────────────────────────────────────────────────────┐
│ Chunk 0: Position 0-1000                                   │
├────────────────────────────────────────────────────────────┤
│ "Executive Summary: Our analysis of Q4 2024 shows          │
│  significant growth in key metrics. Revenue increased by   │
│  23% compared to previous quarter. Customer satisfaction   │
│  improved from 45 to 62 based on NPS scores. Market share  │
│  expanded in three main regions. Detailed breakdown:       │
│  Revenue streams showed strong performance across all      │
│  categories. The digital channel contributed 45% of total  │
│  revenue, up from 38% last quarter..." [1000 chars]        │
└────────────────────────────────────────────────────────────┘
                                                    ▲
                                                    │ End at position 1000

Step 2: Move forward (1000 - 200 = 800)
        Start next chunk at position 800

┌────────────────────────────────────────────────────────────┐
│ Chunk 1: Position 800-1800                                 │
├────────────────────────────────────────────────────────────┤
│ "...Revenue streams showed strong performance across all   │
│  categories. The digital channel contributed 45% of total  │
│  revenue, up from 38% last quarter. Physical stores saw    │
│  12% growth while maintaining profitability margins. New   │
│  product lines launched in Q4 exceeded expectations with   │
│  $2.3M in sales. Strategic partnerships with three major   │
│  retailers expanded our distribution network..." [1000 chars]│
└────────────────────────────────────────────────────────────┘
       ▲                                            ▲
       │                                            │
    Position 800                              Position 1800
    (200 char overlap with Chunk 0)

Step 3: Continue pattern

┌────────────────────────────────────────────────────────────┐
│ Chunk 2: Position 1600-2600                                │
├────────────────────────────────────────────────────────────┤
│ "...Strategic partnerships with three major retailers      │
│  expanded our distribution network significantly. Regional │
│  analysis shows strongest growth in Southeast Asia (+34%)  │
│  followed by Europe (+28%) and North America (+19%).      │
│  Product category breakdown reveals..." [1000 chars]       │
└────────────────────────────────────────────────────────────┘
       ▲
       │ 200 char overlap with Chunk 1

Final chunk (smaller if remaining text < 1000):

┌────────────────────────────────────────────────────────────┐
│ Chunk 3: Position 2400-3000                                │
├────────────────────────────────────────────────────────────┤
│ "...Product category breakdown reveals home goods leading  │
│  with 32% share, followed by electronics at 28%. Outlook   │
│  for Q1 2025 remains positive with projected 15-20% growth │
│  based on current pipeline and market conditions." [600 chars]│
└────────────────────────────────────────────────────────────┘
                                                    ▲
                                                    │ End of document
```

### Overlap Visualization

```
Text Timeline (showing character positions):

0        200      400      600      800      1000     1200     1400
├────────┼────────┼────────┼────────┼────────┼────────┼────────┼────...
│                                             │
│◄──────────── Chunk 0 (1000 chars) ─────────▶│
│                                   ││
│                                   ││◄─ 200 char overlap
│                                   ││
│                                   └┤◄──────── Chunk 1 ────────▶│
│                                    │                  ││
│                                    │                  ││◄─ 200 overlap
│                                    │                  ││
                                     │                  └┤◄───── Chunk 2 ──▶
                                     │                   │
                                     └─ Position 800     └─ Position 1600
                                        (Start Chunk 1)     (Start Chunk 2)
```

## Why 200 Characters Overlap?

### Benefits of Overlap

```
┌─────────────────────────────────────────────────────────────┐
│                   Context Preservation                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Without Overlap:                                           │
│  ┌──────────────────────────┐┌──────────────────────────┐  │
│  │ ...revenue increased by  ││ 23% compared to previous │  │
│  │ significant margins in   ││ quarter due to strong... │  │
│  └──────────────────────────┘└──────────────────────────┘  │
│              ▲                        ▲                     │
│          Chunk 0 ends            Chunk 1 starts             │
│                                                             │
│  Problem:                                                   │
│  • "23%" separated from "revenue increased"                │
│  • Context broken across boundary                          │
│  • Harder to understand each chunk                         │
│                                                             │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                             │
│  With 200 Char Overlap:                                     │
│  ┌──────────────────────────┐                              │
│  │ ...revenue increased by  │                              │
│  │ 23% compared to previous │                              │
│  │ quarter due to strong... │                              │
│  └──────────────────────────┘                              │
│              ▲                                              │
│          Chunk 0 ends with complete thought                │
│                                                             │
│         ┌──────────────────────────┐                       │
│         │ ...revenue increased by  │                       │
│         │ 23% compared to previous │                       │
│         │ quarter due to strong... │                       │
│         └──────────────────────────┘                       │
│              ▲                                              │
│          Chunk 1 starts with context                       │
│                                                             │
│  Benefits:                                                  │
│  ✅ Complete sentences in both chunks                      │
│  ✅ Context maintained                                     │
│  ✅ Better semantic understanding                          │
│  ✅ Improved search relevance                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Overlap Size Trade-offs

```
┌────────────────────────────────────────────────────────────┐
│              Overlap Size Comparison                       │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  No Overlap (0 chars):                                     │
│  ❌ Context loss at boundaries                             │
│  ✅ No data duplication                                    │
│  ✅ Fewer total chunks                                     │
│  Use case: When disk space is critical                    │
│                                                            │
│  Small Overlap (50-100 chars):                             │
│  ⚠️  Partial context preservation                          │
│  ✅ Minimal duplication                                    │
│  Use case: Very large document collections                │
│                                                            │
│  Medium Overlap (200-300 chars):  ◄── OUR CHOICE          │
│  ✅ Good context preservation                              │
│  ✅ Reasonable duplication (~20%)                          │
│  ✅ Better search quality                                  │
│  Use case: Balanced approach (recommended)                │
│                                                            │
│  Large Overlap (500+ chars):                               │
│  ✅ Excellent context                                      │
│  ❌ High duplication (~50%)                                │
│  ❌ More storage, slower indexing                          │
│  Use case: When accuracy is paramount                     │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

## Chunk Size Selection

### Why 1000 Characters?

```
┌────────────────────────────────────────────────────────────┐
│                Chunk Size Analysis                         │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  Too Small (200-300 chars):                                │
│  ┌────────┐                                                │
│  │Fragment│  "...revenue increased by 23% compared..."    │
│  └────────┘                                                │
│  ❌ Incomplete thoughts                                    │
│  ❌ Missing context                                        │
│  ❌ Poor semantic representation                           │
│  ❌ Too many chunks (slow search)                          │
│                                                            │
│  Small (500 chars):                                        │
│  ┌──────────────┐                                          │
│  │   Paragraph  │  "Executive Summary: Our analysis..."   │
│  └──────────────┘                                          │
│  ⚠️  Often incomplete context                              │
│  ⚠️  Many chunks for large documents                       │
│  ✅ Fast embedding generation                              │
│                                                            │
│  Medium (1000 chars):  ◄── OUR CHOICE                     │
│  ┌──────────────────────────┐                             │
│  │   2-3 Paragraphs         │  "Executive Summary:        │
│  │   Complete section       │   Our analysis of Q4...     │
│  │                          │   Key findings include..."   │
│  └──────────────────────────┘                             │
│  ✅ Complete thoughts                                      │
│  ✅ Good context window                                    │
│  ✅ Balanced chunk count                                   │
│  ✅ Optimal for most documents                             │
│                                                            │
│  Large (2000-3000 chars):                                  │
│  ┌────────────────────────────────────┐                   │
│  │       Multiple sections            │                   │
│  │     Mixed topics possible          │                   │
│  └────────────────────────────────────┘                   │
│  ⚠️  May contain multiple topics                           │
│  ⚠️  Less precise retrieval                                │
│  ✅ Fewer chunks (faster indexing)                         │
│                                                            │
│  Too Large (5000+ chars):                                  │
│  ┌──────────────────────────────────────────────┐         │
│  │            Entire chapter/section            │         │
│  │         Many different topics                │         │
│  └──────────────────────────────────────────────┘         │
│  ❌ Topic dilution                                         │
│  ❌ Similar to full document problems                      │
│  ❌ Poor retrieval precision                               │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### Chunk Size in Context

```
Characters  ~Words    ~Sentences   ~Paragraphs   Use Case
─────────────────────────────────────────────────────────────
   200        40          2-3           0.5      ❌ Too fragmented
   500       100          5-6           1-2      ⚠️  Small docs
  1000       200         10-12          2-3      ✅ OPTIMAL (our choice)
  2000       400         20-24          4-6      ⚠️  Large docs
  5000      1000         50-60         10-15     ❌ Too broad

Example of 1000 characters:

┌─────────────────────────────────────────────────────────────┐
│ Executive Summary                                           │
│                                                             │
│ Our analysis of Q4 2024 demonstrates significant growth    │
│ across all key performance indicators. Total revenue       │
│ reached $12.5M, representing a 23% increase compared to    │
│ the previous quarter and 34% year-over-year growth.        │
│                                                             │
│ Customer satisfaction metrics showed remarkable            │
│ improvement, with NPS scores increasing from 45 to 62.     │
│ This improvement correlates with our enhanced customer     │
│ service initiatives launched in September 2024.            │
│                                                             │
│ Market share expanded in three strategic regions:          │
│ Southeast Asia (+34%), Europe (+28%), and North America    │
│ (+19%). The digital sales channel contributed 45% of       │
│ total revenue, up from 38% in Q3.                          │
│                                                             │
│ [~1000 characters - complete, coherent section]            │
└─────────────────────────────────────────────────────────────┘
```

## Real-World Example

### Original PDF Page

```
┌─────────────────────────────────────────────────────────────┐
│                    QUARTERLY REPORT Q4 2024                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ EXECUTIVE SUMMARY                                           │
│                                                             │
│ This quarter demonstrated exceptional performance across   │
│ all business units. Key highlights include revenue growth  │
│ of 23%, customer acquisition increase of 3,450 new users,  │
│ and expansion into two new markets. The product team       │
│ delivered three major feature releases that significantly  │
│ improved user engagement metrics.                           │
│                                                             │
│ FINANCIAL PERFORMANCE                                       │
│                                                             │
│ Revenue: $12.5M (↑23% QoQ, ↑34% YoY)                       │
│ • Digital channel: $5.6M (45% of total)                    │
│ • Retail channel: $4.2M (34% of total)                     │
│ • Enterprise: $2.7M (21% of total)                         │
│                                                             │
│ Operating margin improved to 32%, up from 28% in Q3,       │
│ driven by operational efficiencies and economies of scale. │
│ Net profit reached $4M, representing a 32% profit margin.  │
│                                                             │
│ CUSTOMER METRICS                                            │
│                                                             │
│ Total active users: 145,000 (↑15% QoQ)                     │
│ New user acquisition: 3,450                                │
│ Customer retention rate: 94%                                │
│ Net Promoter Score: 62 (↑from 45)                          │
│                                                             │
│ [~1500 characters total]                                    │
└─────────────────────────────────────────────────────────────┘
```

### How It Gets Chunked

```
Chunk 0 (0-1000 chars):
┌─────────────────────────────────────────────────────────────┐
│ QUARTERLY REPORT Q4 2024                                    │
│                                                             │
│ EXECUTIVE SUMMARY                                           │
│                                                             │
│ This quarter demonstrated exceptional performance across   │
│ all business units. Key highlights include revenue growth  │
│ of 23%, customer acquisition increase of 3,450 new users,  │
│ and expansion into two new markets. The product team       │
│ delivered three major feature releases that significantly  │
│ improved user engagement metrics.                           │
│                                                             │
│ FINANCIAL PERFORMANCE                                       │
│                                                             │
│ Revenue: $12.5M (↑23% QoQ, ↑34% YoY)                       │
│ • Digital channel: $5.6M (45% of total)                    │
│ • Retail channel: $4.2M (34% of total)                     │
│ • Enterprise: $2.7M (21% of total)                         │
│                                                             │
│ Operating margin improved to 32%...                         │
└─────────────────────────────────────────────────────────────┘
    Topics: Executive Summary + Financial Overview
    Good for queries about: "Q4 performance", "revenue", "highlights"

Chunk 1 (800-1800 chars):
┌─────────────────────────────────────────────────────────────┐
│ ...Revenue: $12.5M (↑23% QoQ, ↑34% YoY)                    │
│ • Digital channel: $5.6M (45% of total)                    │
│ • Retail channel: $4.2M (34% of total)                     │
│ • Enterprise: $2.7M (21% of total)                         │
│                                                             │
│ Operating margin improved to 32%, up from 28% in Q3,       │
│ driven by operational efficiencies and economies of scale. │
│ Net profit reached $4M, representing a 32% profit margin.  │
│                                                             │
│ CUSTOMER METRICS                                            │
│                                                             │
│ Total active users: 145,000 (↑15% QoQ)                     │
│ New user acquisition: 3,450                                │
│ Customer retention rate: 94%                                │
│ Net Promoter Score: 62 (↑from 45)                          │
└─────────────────────────────────────────────────────────────┘
    Topics: Financial Details + Customer Metrics
    Good for queries about: "profit margin", "NPS", "user growth"

Note: 200 char overlap ensures "Revenue" context appears in both chunks
```

## Search Example with Chunks

### Query: "What was the customer satisfaction score?"

```
Step 1: Generate query embedding
query_embedding = [0.045, -0.023, 0.078, ...]

Step 2: Search across all chunks
┌─────────────────────────────────────────────────────────────┐
│ All Chunks in Database:                                     │
│                                                             │
│ • quarterly_report_q4_chunk_0 (Executive + Financial)      │
│ • quarterly_report_q4_chunk_1 (Financial + Customers)  ◄─┐ │
│ • quarterly_report_q3_chunk_0 (Previous quarter)          │ │
│ • quarterly_report_q3_chunk_1 (Previous quarter)          │ │
│ • annual_review_chunk_0 (Different doc)                   │ │
│                                                             │ │
└─────────────────────────────────────────────────────────────┘ │
                                                              │
Step 3: HNSW finds most similar chunk ───────────────────────┘

Result:
┌─────────────────────────────────────────────────────────────┐
│ Best Match: quarterly_report_q4_chunk_1                     │
│ Similarity: 0.89 (89% similar to query)                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ CUSTOMER METRICS                                            │
│                                                             │
│ Total active users: 145,000 (↑15% QoQ)                     │
│ New user acquisition: 3,450                                │
│ Customer retention rate: 94%                                │
│ Net Promoter Score: 62 (↑from 45)  ◄── ANSWER HERE         │
│                                                             │
└─────────────────────────────────────────────────────────────┘

✅ Precise retrieval - exact section with the answer
✅ No need to read entire document
✅ Fast and accurate
```

## Implementation Code

```python
def chunk_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
    """
    Split text into overlapping chunks.

    Args:
        text: Input text to chunk
        chunk_size: Target size of each chunk in characters
        chunk_overlap: Number of characters to overlap between chunks

    Returns:
        List of text chunks
    """
    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        # Extract chunk from start to start+chunk_size
        end = start + chunk_size
        chunk = text[start:end]

        chunks.append(chunk)

        # Move start forward by (chunk_size - chunk_overlap)
        # This creates the overlap
        start += (chunk_size - chunk_overlap)

        # Prevent infinite loop if chunk_overlap >= chunk_size
        if chunk_overlap >= chunk_size:
            break

    return chunks


# Example usage:
text = "Long document text..." * 1000  # ~15,000 chars
chunks = chunk_text(text, chunk_size=1000, chunk_overlap=200)

print(f"Total text length: {len(text)} characters")
print(f"Number of chunks: {len(chunks)}")
print(f"Chunk 0 length: {len(chunks[0])}")
print(f"Chunk 1 length: {len(chunks[1])}")

# Verify overlap
overlap_text = chunks[0][-200:]  # Last 200 chars of chunk 0
chunk1_start = chunks[1][:200]    # First 200 chars of chunk 1
print(f"Overlap verified: {overlap_text == chunk1_start}")
```

## Optimization Tips

### 1. Adjust for Document Type

```
Technical Documents (code, specs):
• Smaller chunks (500-700 chars)
• Less overlap (100-150 chars)
• Preserve code blocks

Narrative Documents (reports, articles):
• Medium chunks (1000-1500 chars) ◄── DEFAULT
• Medium overlap (200-300 chars)
• Preserve paragraph boundaries

Legal Documents:
• Larger chunks (1500-2000 chars)
• More overlap (300-400 chars)
• Preserve section context
```

### 2. Smart Boundary Detection

```python
def chunk_text_smart(text: str, chunk_size: int = 1000,
                     chunk_overlap: int = 200) -> List[str]:
    """
    Improved chunking that respects sentence boundaries.
    """
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size

        # Try to find sentence boundary near target end
        if end < len(text):
            # Look for period followed by space within next 100 chars
            for i in range(end, min(end + 100, len(text))):
                if text[i:i+2] in ['. ', '.\n', '! ', '? ']:
                    end = i + 2
                    break

        chunk = text[start:end]
        chunks.append(chunk)

        start += (chunk_size - chunk_overlap)

    return chunks
```

### 3. Metadata-Aware Chunking

```python
def chunk_with_metadata(text: str, page_num: int,
                       chunk_size: int = 1000) -> List[Dict]:
    """
    Chunk with metadata preservation.
    """
    chunks = chunk_text(text, chunk_size)

    return [
        {
            "text": chunk,
            "page_num": page_num,
            "chunk_index": i,
            "char_start": i * (chunk_size - 200),
            "char_end": i * (chunk_size - 200) + len(chunk)
        }
        for i, chunk in enumerate(chunks)
    ]
```

## Summary

**Chunking Strategy:**
- **Size**: 1000 characters (2-3 paragraphs)
- **Overlap**: 200 characters (20%)
- **Purpose**: Balance context and precision

**Key Benefits:**
1. ✅ Preserves semantic context
2. ✅ Enables precise retrieval
3. ✅ Optimal for vector search
4. ✅ Efficient processing
5. ✅ Scalable approach

**Trade-offs Managed:**
- Context preservation vs storage efficiency
- Chunk granularity vs search speed
- Overlap size vs data duplication

**Best Practices:**
1. Adjust chunk size based on document type
2. Use overlap to maintain context
3. Consider sentence/paragraph boundaries
4. Test and tune for your specific use case
5. Monitor retrieval quality and adjust accordingly

