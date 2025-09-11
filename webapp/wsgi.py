#!/usr/bin/env python3
"""
Production WSGI entry point for the FPL webapp
"""
from app import app
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


if __name__ == "__main__":
    app.run()
