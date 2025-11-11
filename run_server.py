#!/usr/bin/env python3
"""
Quick start script for PDF Vector DB MCP Server
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.mcp_server import mcp

if __name__ == "__main__":
    print("Starting PDF Vector DB MCP Server...")
    print("Press Ctrl+C to stop")
    try:
        mcp.run()
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)
