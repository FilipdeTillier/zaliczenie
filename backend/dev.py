#!/usr/bin/env python3
"""
Development server script for hot reload functionality.
Run this script for local development outside of Docker.
"""

import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        reload_dirs=["/app", "."],
        log_level="info"
    ) 