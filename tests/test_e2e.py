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
def test_processes_multilingual_pdf(
    e2e_test_pdf: Path,
    mistral_client: Mistral,
    tmp_path: Path,
) -> None:
    """Should process multilingual PDF through full pipeline with feature preservation.

    Tests the complete OCR → translate → render pipeline, asserting that
    key document features are preserved throughout.
    """
    # === Execute pipeline ===
    ocr_result = extract_pdf(e2e_test_pdf, mistral_client)
    translated_md = translate_markdown(ocr_result.raw_markdown, mistral_client)
    output_path = tmp_path / "output.pdf"
    render_pdf(
        translated_md,
        output_path,
        images=ocr_result.images,
        page_dimensions=ocr_result.page_dimensions,
    )

    # === Structural assertions ===
    assert output_path.exists()
    assert output_path.stat().st_size > 1000
    assert len(ocr_result.pages) == 2
    assert len(ocr_result.images) == 3

    # === Page dimensions (A4) ===
    assert ocr_result.page_dimensions is not None
    assert ocr_result.page_dimensions.width_mm == pytest.approx(210, rel=0.01)
    assert ocr_result.page_dimensions.height_mm == pytest.approx(297, rel=0.01)

    # === Image metadata ===
    img_widths = {i.image_id: i.width_percent for i in ocr_result.images}
    assert img_widths["img-0.jpeg"] == pytest.approx(54.8, rel=0.1)
    assert img_widths["img-1.jpeg"] == pytest.approx(54.8, rel=0.1)
    assert img_widths["img-2.jpeg"] == pytest.approx(7.5, rel=0.1)

    # === Content preservation ===
    assert "data:image" in translated_md  # Base64 images
    assert "<table" in translated_md.lower()  # HTML tables
    assert "rowspan" in translated_md.lower()  # Merged cells
    assert "colspan" in translated_md.lower()
    assert "€" in translated_md  # Special characters

    # === Translation verification ===
    assert "resources and links" in translated_md.lower()  # French → English
    assert "january" in translated_md.lower()  # Italian → English

    # === Markdown formatting (OCR dependent) ===
    assert "**" in translated_md  # Bold
    assert "*" in translated_md  # Italic
    assert "#" in translated_md  # Headers
    assert "google" in translated_md.lower()  # Link text
