# PDF Vector DB MCP Server

A Model Context Protocol (MCP) server that provides RAG (Retrieval-Augmented Generation) capabilities for PDF documents. This server automatically indexes PDF files, generates embeddings using sentence-transformers (all-mpnet-base-v2), stores them in ChromaDB, and provides semantic search tools for LLMs to query the documents. **No API key required - everything runs locally!**

## Features

- **Automatic PDF Indexing**: Monitors a folder and automatically indexes new/modified PDFs
- **Semantic Search**: Query documents using natural language
- **Source Citations**: Returns results with document names and page numbers
- **Multiple MCP Tools**: Query, list, and manage indexed documents
- **ChromaDB Vector Store**: Efficient local vector database with persistence
- **Local Embeddings**: Uses sentence-transformers (all-mpnet-base-v2) - no API key needed!
- **100% Privacy**: Everything runs on your machine, no cloud dependencies
- **Completely Free**: No API costs, no subscriptions
- **Offline Capable**: Works without internet after initial setup
- **File Watching**: Real-time monitoring and re-indexing of PDF changes
- **Smart Chunking**: Intelligent text splitting with overlap for better context

## Why This Server?

✅ **No API Key Required** - Start using it immediately
✅ **100% Local & Private** - Your data never leaves your machine
✅ **Zero Cost** - Completely free to run
✅ **High Quality** - all-mpnet-base-v2 produces excellent 768-dimensional embeddings
✅ **Offline First** - Works without internet after model download (~420MB one-time)

## Architecture

```
pdf-vectordb-mcp/
├── src/
│   ├── config.py              # Configuration management
│   ├── pdf_processor.py       # PDF extraction and chunking
│   ├── embeddings.py          # OpenAI embedding generation
│   ├── vector_store.py        # ChromaDB operations
│   ├── file_watcher.py        # File system monitoring
│   ├── mcp_server.py          # MCP server implementation
│   └── utils.py               # Helper functions
├── data/
│   ├── pdfs/                  # Place your PDF files here
│   └── chroma_db/             # ChromaDB persistence
├── requirements.txt
├── .env                       # Your configuration
└── README.md
```

## Installation

### Prerequisites

- Python 3.10 or higher
- OpenAI API key

### Setup Steps

1. **Clone or download this repository**

2. **Create a virtual environment**

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure environment variables**

Copy `.env.example` to `.env` and fill in your settings:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
OPENAI_API_KEY=sk-your-openai-api-key-here
PDF_FOLDER=./data/pdfs
CHROMA_DB_PATH=./data/chroma_db
EMBEDDING_MODEL=text-embedding-3-small
CHUNK_SIZE=800
CHUNK_OVERLAP=200
DEFAULT_TOP_K=5
LOG_LEVEL=INFO
```

5. **Add your PDF files**

Place PDF files in the `data/pdfs/` folder. They will be automatically indexed when the server starts.

## Usage

### Running the MCP Server

```bash
python -m src.mcp_server
```

The server will:
1. Validate your configuration
2. Index any existing PDFs in the `data/pdfs/` folder
3. Start monitoring the folder for changes
4. Start the MCP server ready to accept tool calls

### Connecting to Claude Desktop

Add this configuration to your Claude Desktop config file:

**On Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
**On macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "pdf-vectordb": {
      "command": "python",
      "args": [
        "-m",
        "src.mcp_server"
      ],
      "cwd": "C:\\Users\\arif\\PycharmProjects\\pdf-vectordb-mcp",
      "env": {
        "OPENAI_API_KEY": "your-openai-api-key-here"
      }
    }
  }
}
```

Update the `cwd` path to match your project location.

## MCP Tools

### 1. query_documents

Search through indexed PDF documents using natural language.

**Parameters:**
- `query` (required): Natural language search query
- `top_k` (optional): Number of results to return (default: 5)
- `document` (optional): Filter results to specific document

**Example:**
```
Query: "What are the key findings about climate change?"
```

**Returns:**
- Relevant text chunks with source citations
- Page numbers and document names
- Relevance scores

### 2. list_documents

List all indexed PDF documents with statistics.

**Parameters:** None

**Returns:**
- Document names
- Number of pages per document
- Number of chunks per document

### 3. get_document_info

Get detailed information about a specific document.

**Parameters:**
- `document` (required): Name of the document

**Returns:**
- Total pages
- Total chunks
- List of page numbers

### 4. reindex_document

Manually trigger re-indexing of a specific PDF.

**Parameters:**
- `document` (required): Name of the PDF file

**Use cases:**
- Force re-processing after manual edits
- Recover from indexing errors

### 5. get_system_stats

Get overall system statistics and configuration.

**Parameters:** None

**Returns:**
- Total documents and chunks
- Current configuration settings
- File watcher status

## Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | Required |
| `PDF_FOLDER` | Directory containing PDFs | `./data/pdfs` |
| `CHROMA_DB_PATH` | ChromaDB storage location | `./data/chroma_db` |
| `EMBEDDING_MODEL` | OpenAI embedding model | `text-embedding-3-small` |
| `CHUNK_SIZE` | Characters per chunk | `800` |
| `CHUNK_OVERLAP` | Overlapping characters | `200` |
| `DEFAULT_TOP_K` | Default search results | `5` |
| `LOG_LEVEL` | Logging level | `INFO` |

### Chunking Strategy

The system uses intelligent chunking with:
- **Sentence boundary detection**: Prefers breaking at sentence ends
- **Word boundary fallback**: Falls back to word boundaries
- **Overlap**: Maintains context across chunks
- **Metadata preservation**: Tracks document name, page number, chunk index

## How It Works

### 1. PDF Processing Pipeline

```
PDF File → Text Extraction → Smart Chunking → Embedding Generation → Vector Store
```

1. **Text Extraction**: Extracts text page-by-page using pypdf
2. **Cleaning**: Removes artifacts and normalizes whitespace
3. **Chunking**: Splits text into overlapping chunks
4. **Embedding**: Generates OpenAI embeddings for each chunk
5. **Storage**: Stores in ChromaDB with metadata

### 2. Query Pipeline

```
Query → Generate Embedding → Similarity Search → Rank Results → Return with Sources
```

1. **Query Embedding**: Converts query to vector
2. **Similarity Search**: Finds similar chunks using cosine similarity
3. **Ranking**: Orders by relevance score
4. **Source Attribution**: Includes document and page information

### 3. File Watching

The server monitors the PDF folder and:
- **On Create**: Automatically indexes new PDFs
- **On Modify**: Re-indexes changed PDFs
- **On Delete**: Removes from vector store
- **Debouncing**: Waits for file writes to complete

## Advanced Usage

### Custom Embedding Models

You can use different OpenAI embedding models:

```env
# Smaller, faster, cheaper
EMBEDDING_MODEL=text-embedding-3-small

# Larger, more accurate, more expensive
EMBEDDING_MODEL=text-embedding-3-large
```

### Adjusting Chunk Size

For different document types:

```env
# Technical documents with dense information
CHUNK_SIZE=500
CHUNK_OVERLAP=100

# Narrative documents
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

### Batch Re-indexing

To re-index all documents:

1. Stop the server
2. Delete the `data/chroma_db/` folder
3. Restart the server

## Troubleshooting

### PDFs Not Being Indexed

- Check that PDFs are in the correct folder (`data/pdfs/`)
- Ensure PDFs are not password-protected
- Check logs for extraction errors
- Verify file permissions

### OpenAI API Errors

- Verify your API key is correct
- Check your OpenAI account has available credits
- Review rate limits if processing many documents

### ChromaDB Issues

- Ensure `data/chroma_db/` directory is writable
- Check disk space
- Try deleting and recreating the database

### Memory Issues

For large PDF collections:
- Process in batches
- Increase system RAM
- Use smaller chunk sizes

## Development

### Running Tests

```bash
pytest tests/
```

### Logging

Logs are written to:
- Console output
- `pdf_vectordb_mcp.log` file

Adjust log level in `.env`:

```env
LOG_LEVEL=DEBUG  # For detailed debugging
LOG_LEVEL=INFO   # Normal operation
LOG_LEVEL=WARNING # Only warnings and errors
```

## Performance Considerations

### Embedding Costs

OpenAI embedding costs (as of 2024):
- `text-embedding-3-small`: ~$0.02 per 1M tokens
- `text-embedding-3-large`: ~$0.13 per 1M tokens

A typical PDF page (~500 words) costs less than $0.001 to embed.

### Processing Speed

- PDF extraction: ~1-2 seconds per document
- Embedding generation: ~1-2 seconds per batch (100 chunks)
- Vector storage: ~0.1 seconds per document

### Storage

- ChromaDB: ~1-2 KB per chunk
- A 100-page PDF typically generates 200-400 chunks (~400-800 KB)

## Limitations

- **PDF Support**: Text-based PDFs only (no OCR for scanned documents)
- **Languages**: Works best with English (depends on embedding model)
- **File Size**: Large PDFs (>1000 pages) may take time to process
- **Concurrent Access**: Single-server architecture

## Future Enhancements

Potential improvements:
- OCR support for scanned PDFs
- Table extraction and special handling
- Image/diagram description
- Multi-modal embeddings
- Hybrid search (vector + keyword)
- Re-ranking with cross-encoders
- Query expansion and rewriting
- Document summarization tool
- Support for other document formats (Word, etc.)

## License

MIT License - feel free to use and modify for your needs.

## Contributing

Contributions welcome! Please feel free to submit issues and pull requests.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review logs in `pdf_vectordb_mcp.log`
3. Open an issue on GitHub

## Acknowledgments

- Built with [MCP](https://modelcontextprotocol.io/)
- Uses [ChromaDB](https://www.trychroma.com/) for vector storage
- Powered by [OpenAI Embeddings](https://platform.openai.com/docs/guides/embeddings)
- PDF processing with [pypdf](https://pypdf.readthedocs.io/)
