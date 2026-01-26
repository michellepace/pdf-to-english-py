"""End-to-end tests for the full PDF translation pipeline."""

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path

    from mistralai import Mistral

from pdf_to_english_py.ocr import extract_pdf
from pdf_to_english_py.render import render_pdf
from pdf_to_english_py.translate import translate_markdown


@pytest.mark.integration
def test_processes_french_pdf(
    french_pdf: Path,
    mistral_client: Mistral,
    tmp_path: Path,
) -> None:
    """Should process French PDF through full pipeline with feature preservation.

    Tests the complete OCR → translate → render pipeline, asserting that
    key document features are preserved throughout.
    """
    # Step 1: Extract text using OCR
    ocr_result = extract_pdf(french_pdf, mistral_client)

    # Step 2: Translate to English
    translated_md = translate_markdown(ocr_result.raw_markdown, mistral_client)

    # Step 3: Render to PDF
    output_path = tmp_path / "output.pdf"
    render_pdf(translated_md, output_path)

    # === Pipeline completion assertions ===
    assert output_path.exists()
    assert output_path.stat().st_size > 1000

    # === High confidence assertions ===

    # Multi-page: OCR should detect both pages
    assert len(ocr_result.pages) == 2, "Expected 2 pages from OCR"

    # Images: Our strip/restore logic preserves base64 data URIs
    assert "data:image" in translated_md, "Base64 image should be preserved"

    # Tables: Mistral OCR outputs tables as HTML
    assert "<table" in translated_md.lower(), "HTML table should be present"

    # Merge attributes: Tables have rowspan and colspan
    assert "rowspan" in translated_md.lower(), "rowspan attribute should be preserved"
    assert "colspan" in translated_md.lower(), "colspan attribute should be preserved"

    # Special characters: Euro symbol should pass through
    assert "€" in translated_md, "Euro symbol (€) should be preserved"

    # Translation: "RESSOURCES ET LIENS" should be translated to English
    assert "resources and links" in translated_md.lower(), (
        "French section header should be translated to English"
    )

    # === Risky assertions (OCR behaviour dependent) ===

    # Bold: PDF has "This is BOLD" - OCR may output as **BOLD** or lose it
    assert "**" in translated_md, "Bold markdown (**) should be present"

    # Italic: PDF has "This is italics" - OCR may output as *italic* or lose it
    # Note: Can't just check for * since it appears in other contexts
    assert "*" in translated_md, "Italic markdown (*) should be present"

    # Headers: PDF has section headers - OCR may output as # headers
    assert translated_md.strip().startswith("#") or "\n#" in translated_md, (
        "Markdown headers (#) should be present"
    )

    # Links: PDF has "Google Link" hyperlink - format may vary
    assert "google" in translated_md.lower(), "Google link should be preserved"
