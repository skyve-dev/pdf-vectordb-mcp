# Quick Start Guide

Get your PDF RAG MCP server running in 3 minutes - **NO API KEY NEEDED**!

## Prerequisites

- Python 3.10+
- That's it! No API keys, no subscriptions, no cloud accounts

## Setup (3 steps)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs everything needed, including sentence-transformers for local embeddings (~420MB on first run).

### 2. (Optional) Configure Settings

The `.env` file is already configured with sensible defaults:

```env
EMBEDDING_MODEL=all-mpnet-base-v2  # Local model, no API needed
EMBEDDING_DEVICE=auto              # Auto-detects GPU or uses CPU
```

**Optional tweaks:**
- Use GPU: `EMBEDDING_DEVICE=cuda` (much faster!)
- Use CPU: `EMBEDDING_DEVICE=cpu` (works on any machine)

### 3. Add PDFs

Place your PDF files in `data/pdfs/`:

```bash
# Copy your PDFs
cp ~/Documents/*.pdf data/pdfs/
```

### 4. Run the Server

```bash
python run_server.py
```

You should see:
```
Starting PDF Vector DB MCP Server...
INFO - Initialized VectorStore...
INFO - Indexing 3 existing PDFs...
INFO - Started watching directory...
```

### 5. Connect to Claude Desktop

Edit your Claude Desktop config:

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

Add:

```json
{
  "mcpServers": {
    "pdf-vectordb": {
      "command": "python",
      "args": ["-m", "src.mcp_server"],
      "cwd": "/full/path/to/pdf-vectordb-mcp"
    }
  }
}
```

Replace `/full/path/to/pdf-vectordb-mcp` with your actual project path.

Restart Claude Desktop.

## Usage

In Claude Desktop, try these queries:

```
"What PDFs are indexed?"
→ Uses list_documents tool

"Search for information about project requirements"
→ Uses query_documents tool

"Tell me about requirements.pdf"
→ Uses get_document_info tool
```

## What Happens Automatically

- ✅ Extracts text from all PDFs
- ✅ Chunks text intelligently
- ✅ Generates embeddings locally (all-mpnet-base-v2)
- ✅ Stores in ChromaDB
- ✅ Watches for new/modified PDFs
- ✅ Re-indexes automatically

### First Run - Model Download

On first run, sentence-transformers will download the model (~420MB). This only happens once:

```
Downloading model all-mpnet-base-v2...
Model cached at ~/.cache/torch/sentence_transformers/
```

After that, everything runs 100% offline!

## Common Issues

### Slow first run
→ Normal - downloading model (~420MB one-time)
→ Subsequent runs are much faster
→ Model is cached permanently

### Slow indexing
→ Use GPU if available: `EMBEDDING_DEVICE=cuda` (10-20x faster!)
→ CPU mode works but takes longer (2-5 minutes per 100 pages)

### "No documents are currently indexed"
→ Make sure PDFs are in `data/pdfs/` folder
→ Check logs for extraction errors: `tail -f pdf_vectordb_mcp.log`

## Next Steps

- Read the full [README.md](README.md) for advanced configuration
- Adjust chunk size for your document types
- Try different embedding models
- Add more PDFs and see automatic indexing in action!

## Getting Help

Check the logs:
```bash
tail -f pdf_vectordb_mcp.log
```

Still stuck? Open an issue on GitHub with:
- Error message from logs
- Your `.env` settings (without API key!)
- Steps to reproduce
