"""Tests for OCR module."""

import base64
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path

from pdf_to_english_py.ocr import (
    ImageMetadata,
    OcrPage,
    OcrResult,
    combine_pages,
    encode_pdf_to_base64,
    inline_images,
    inline_tables,
)


class TestEncodePdfToBase64:
    """Tests for encode_pdf_to_base64 function."""

    def test_encodes_pdf_file_to_base64_string(self, tmp_path: Path) -> None:
        """A PDF file should be encoded to a valid base64 string."""
        # Create a minimal test file
        test_file = tmp_path / "test.pdf"
        test_content = b"%PDF-1.4 test content"
        test_file.write_bytes(test_content)

        result = encode_pdf_to_base64(test_file)

        # Should be valid base64
        decoded = base64.b64decode(result)
        assert decoded == test_content

    def test_raises_error_for_nonexistent_file(self, tmp_path: Path) -> None:
        """Should raise FileNotFoundError for missing file."""
        nonexistent = tmp_path / "missing.pdf"

        with pytest.raises(FileNotFoundError):
            encode_pdf_to_base64(nonexistent)


class TestInlineTables:
    """Tests for inline_tables function."""

    def test_replaces_single_table_placeholder(self) -> None:
        """A single table placeholder should be replaced with HTML content."""
        markdown = "Text before\n\n[tbl-0.html](tbl-0.html)\n\nText after"
        tables = [
            {
                "id": "tbl-0.html",
                "content": "<table><tr><td>Cell</td></tr></table>",
                "format": "html",
            }
        ]

        result = inline_tables(markdown, tables)

        assert "[tbl-0.html](tbl-0.html)" not in result
        assert "<table><tr><td>Cell</td></tr></table>" in result
        assert "Text before" in result
        assert "Text after" in result

    def test_replaces_multiple_table_placeholders(self) -> None:
        """Multiple table placeholders should all be replaced."""
        markdown = "[tbl-0.html](tbl-0.html)\n\n[tbl-1.html](tbl-1.html)"
        tables = [
            {"id": "tbl-0.html", "content": "<table><tr><td>First</td></tr></table>"},
            {"id": "tbl-1.html", "content": "<table><tr><td>Second</td></tr></table>"},
        ]

        result = inline_tables(markdown, tables)

        assert "[tbl-0.html]" not in result
        assert "[tbl-1.html]" not in result
        assert "First" in result
        assert "Second" in result

    def test_preserves_colspan_rowspan_attributes(self) -> None:
        """HTML table attributes like colspan and rowspan should be preserved."""
        markdown = "[tbl-0.html](tbl-0.html)"
        tables = [
            {
                "id": "tbl-0.html",
                "content": '<table><tr><th colspan="2">Header</th></tr>'
                '<tr><td rowspan="2">Merged</td><td>A</td></tr></table>',
            }
        ]

        result = inline_tables(markdown, tables)

        assert 'colspan="2"' in result
        assert 'rowspan="2"' in result

    def test_returns_unchanged_if_no_tables(self) -> None:
        """Markdown without table placeholders should be unchanged."""
        markdown = "Just some text without tables."
        tables: list[dict[str, str]] = []

        result = inline_tables(markdown, tables)

        assert result == markdown


class TestInlineImages:
    """Tests for inline_images function."""

    def test_replaces_single_image_placeholder(self) -> None:
        """A single image placeholder should be replaced with base64 data URI."""
        markdown = "![img-0.jpeg](img-0.jpeg)"
        images = [
            {
                "id": "img-0.jpeg",
                "image_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRg==",
            }
        ]

        result = inline_images(markdown, images)

        assert "![img-0.jpeg](img-0.jpeg)" not in result
        assert "![img-0.jpeg](data:image/jpeg;base64,/9j/4AAQSkZJRg==)" in result

    def test_replaces_multiple_image_placeholders(self) -> None:
        """Multiple image placeholders should all be replaced."""
        markdown = "![img-0.jpeg](img-0.jpeg)\n\n![img-1.png](img-1.png)"
        images = [
            {"id": "img-0.jpeg", "image_base64": "data:image/jpeg;base64,AAAA"},
            {"id": "img-1.png", "image_base64": "data:image/png;base64,BBBB"},
        ]

        result = inline_images(markdown, images)

        assert "![img-0.jpeg](data:image/jpeg;base64,AAAA)" in result
        assert "![img-1.png](data:image/png;base64,BBBB)" in result

    def test_returns_unchanged_if_no_images(self) -> None:
        """Markdown without image placeholders should be unchanged."""
        markdown = "Just some text without images."
        images: list[dict[str, str]] = []

        result = inline_images(markdown, images)

        assert result == markdown


class TestImageMetadata:
    """Tests for ImageMetadata dataclass."""

    def test_stores_image_id_and_width_percent(self) -> None:
        """ImageMetadata should store image_id and width_percent."""
        metadata = ImageMetadata(image_id="img-0.jpeg", width_percent=23.8)
        assert metadata.image_id == "img-0.jpeg"
        assert metadata.width_percent == 23.8

    def test_calculates_width_percent_from_bounding_box(self) -> None:
        """Should calculate width_percent from bounding box coordinates."""
        metadata = ImageMetadata.from_bounding_box(
            image_id="img-0.jpeg",
            top_left_x=152,
            bottom_right_x=276,
            page_width=1654,
        )
        assert metadata.width_percent == pytest.approx(7.5, rel=0.01)


class TestOcrResultWithMetadata:
    """Tests for OcrResult with image metadata."""

    def test_ocr_result_stores_image_metadata(self) -> None:
        """OcrResult should store image metadata."""
        images = [ImageMetadata(image_id="img-0.jpeg", width_percent=7.5)]
        result = OcrResult(pages=[], raw_markdown="", images=images)
        assert len(result.images) == 1

    def test_ocr_result_defaults_to_empty_images(self) -> None:
        """OcrResult should default to empty images list."""
        result = OcrResult(pages=[], raw_markdown="")
        assert result.images == []


class TestOcrDataClasses:
    """Tests for OcrPage and OcrResult data classes."""

    def test_ocr_page_stores_index_and_markdown(self) -> None:
        """OcrPage should store page index and markdown content."""
        page = OcrPage(index=0, markdown="# Title\n\nContent here.")

        assert page.index == 0
        assert page.markdown == "# Title\n\nContent here."

    def test_ocr_result_stores_pages_and_raw_markdown(self) -> None:
        """OcrResult should store list of pages and combined raw markdown."""
        pages = [
            OcrPage(index=0, markdown="Page 1"),
            OcrPage(index=1, markdown="Page 2"),
        ]
        result = OcrResult(pages=pages, raw_markdown="Page 1\n\nPage 2")

        assert len(result.pages) == 2
        assert result.raw_markdown == "Page 1\n\nPage 2"


class TestCombinePages:
    """Tests for combine_pages helper function."""

    def test_joins_pages_with_horizontal_rule_separator(self) -> None:
        """Multiple pages should be joined with --- separator."""
        pages = [
            OcrPage(index=0, markdown="Page 1 content"),
            OcrPage(index=1, markdown="Page 2 content"),
        ]

        result = combine_pages(pages)

        assert result == "Page 1 content\n\n---\n\nPage 2 content"

    def test_single_page_has_no_separator(self) -> None:
        """Single page should not have separator."""
        pages = [OcrPage(index=0, markdown="Only page")]

        result = combine_pages(pages)

        assert result == "Only page"
        assert "---" not in result
