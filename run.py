"""Entry point for Railway deployment."""

import sys
from pathlib import Path

# Add src to Python path so imports work
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pdf_to_english_py.app import main

if __name__ == "__main__":
    main()
