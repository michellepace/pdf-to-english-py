"""Shared test fixtures."""

import os
from pathlib import Path

import pytest
from dotenv import load_dotenv
from mistralai import Mistral

load_dotenv()


@pytest.fixture
def project_root() -> Path:
    """Path to the project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def sample_pdfs_dir(project_root: Path) -> Path:
    """Path to sample PDFs directory."""
    return project_root / "sample_pdfs"


@pytest.fixture
def french_pdf(sample_pdfs_dir: Path) -> Path:
    """Path to French test PDF with tables, links, and pictures."""
    pdf_path = sample_pdfs_dir / "french.pdf"
    if not pdf_path.exists():
        pytest.skip(f"Test PDF not found: {pdf_path}")
    return pdf_path


@pytest.fixture
def mistral_client() -> Mistral:
    """Configured Mistral client from environment.

    Skips tests if MISTRAL_API_KEY is not set.
    """
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        pytest.skip("MISTRAL_API_KEY not set")
    return Mistral(api_key=api_key)
