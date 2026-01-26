"""Tests for render module."""

from typing import TYPE_CHECKING

from pdf_to_english_py.render import (
    html_to_pdf,
    markdown_to_html,
    render_pdf,
    wrap_with_styles,
)

if TYPE_CHECKING:
    from pathlib import Path


class TestMarkdownToHtml:
    """Tests for markdown_to_html function."""

    def test_converts_headers(self) -> None:
        """Markdown headers should be converted to HTML headers."""
        markdown = "# Title\n\n## Subtitle"

        result = markdown_to_html(markdown)

        assert "<h1>" in result
        assert "Title" in result
        assert "<h2>" in result
        assert "Subtitle" in result

    def test_converts_paragraphs(self) -> None:
        """Text should be wrapped in paragraph tags."""
        markdown = "This is a paragraph."

        result = markdown_to_html(markdown)

        assert "<p>" in result
        assert "This is a paragraph." in result

    def test_preserves_embedded_html_table(self) -> None:
        """HTML tables embedded in markdown should pass through unchanged."""
        markdown = """# Title

<table>
<tr><th>Header</th></tr>
<tr><td>Cell</td></tr>
</table>

More text.
"""
        result = markdown_to_html(markdown)

        assert "<table>" in result
        assert "<tr>" in result
        assert "<th>Header</th>" in result
        assert "<td>Cell</td>" in result

    def test_preserves_colspan_rowspan(self) -> None:
        """HTML table attributes like colspan and rowspan should be preserved."""
        markdown = """<table>
<tr><th colspan="2">Merged Header</th></tr>
<tr><td rowspan="2">Vertical</td><td>A</td></tr>
<tr><td>B</td></tr>
</table>
"""
        result = markdown_to_html(markdown)

        assert 'colspan="2"' in result
        assert 'rowspan="2"' in result

    def test_converts_bold_and_italic(self) -> None:
        """Bold and italic markdown should be converted to HTML."""
        markdown = "Text with **bold** and *italic*."

        result = markdown_to_html(markdown)

        assert "<strong>bold</strong>" in result
        assert "<em>italic</em>" in result

    def test_converts_lists(self) -> None:
        """Markdown lists should be converted to HTML lists."""
        markdown = """- First item
- Second item
"""
        result = markdown_to_html(markdown)

        assert "<ul>" in result
        assert "<li>" in result
        assert "First item" in result

    def test_preserves_base64_image(self) -> None:
        """Base64 image references should be converted to img tags."""
        base64_img = (
            "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcS"
            "JAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
        )
        markdown = f"![test image]({base64_img})"

        result = markdown_to_html(markdown)

        assert "<img" in result
        assert base64_img in result


class TestWrapWithStyles:
    """Tests for wrap_with_styles function."""

    def test_wraps_with_html_structure(self) -> None:
        """Should wrap content with full HTML document structure."""
        html_body = "<h1>Title</h1><p>Content</p>"

        result = wrap_with_styles(html_body)

        assert "<!DOCTYPE html>" in result or "<html" in result
        assert "<head>" in result
        assert "<body>" in result
        assert "</html>" in result

    def test_includes_css_styles(self) -> None:
        """Should include CSS styles in the document."""
        html_body = "<p>Content</p>"

        result = wrap_with_styles(html_body)

        assert "<style>" in result
        # Should have body styling
        assert "font-family" in result
        # Should have table styling
        assert "border" in result

    def test_preserves_body_content(self) -> None:
        """Body content should be preserved in the output."""
        html_body = "<h1>My Title</h1><p>My paragraph.</p>"

        result = wrap_with_styles(html_body)

        assert "<h1>My Title</h1>" in result
        assert "<p>My paragraph.</p>" in result


class TestHtmlToPdf:
    """Tests for html_to_pdf function."""

    def test_creates_pdf_file(self, tmp_path: Path) -> None:
        """Should create a PDF file at the specified path."""
        html = """<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body><h1>Hello World</h1></body>
</html>
"""
        output_path = tmp_path / "test.pdf"

        result = html_to_pdf(html, output_path)

        assert result == output_path
        assert output_path.exists()
        assert output_path.stat().st_size > 0

    def test_pdf_contains_content(self, tmp_path: Path) -> None:
        """Generated PDF should have reasonable size (contains content)."""
        html = """<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body>
<h1>Test Document</h1>
<p>This is a test paragraph with some content.</p>
<table>
<tr><td>Cell 1</td><td>Cell 2</td></tr>
</table>
</body>
</html>
"""
        output_path = tmp_path / "test.pdf"

        html_to_pdf(html, output_path)

        # PDF with content should be at least 1KB
        assert output_path.stat().st_size > 1000

    def test_pdf_with_base64_image(self, tmp_path: Path) -> None:
        """PDF should be generated successfully with embedded base64 images."""
        # Small 1x1 red pixel PNG
        base64_img = (
            "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcS"
            "JAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
        )
        html = f"""<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body>
<h1>Image Test</h1>
<img src="{base64_img}" alt="test">
</body>
</html>
"""
        output_path = tmp_path / "test.pdf"

        html_to_pdf(html, output_path)

        assert output_path.exists()
        assert output_path.stat().st_size > 0


class TestRenderPdf:
    """Tests for render_pdf convenience function."""

    def test_full_pipeline_from_markdown(self, tmp_path: Path) -> None:
        """Should render markdown directly to PDF."""
        markdown = """# Test Document

This is a test paragraph.

<table>
<tr><th>Header</th></tr>
<tr><td>Cell</td></tr>
</table>
"""
        output_path = tmp_path / "output.pdf"

        result = render_pdf(markdown, output_path)

        assert result == output_path
        assert output_path.exists()
        assert output_path.stat().st_size > 1000

    def test_renders_complex_document(self, tmp_path: Path) -> None:
        """Should handle complex documents with multiple elements."""
        base64_img = (
            "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcS"
            "JAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
        )
        markdown = f"""# Complex Document

## Introduction

This document has **bold** and *italic* text.

## Table Section

<table>
<tr><th colspan="2">Merged Header</th></tr>
<tr><td>A</td><td>B</td></tr>
</table>

## Image Section

![test]({base64_img})

## List Section

- Item 1
- Item 2
- Item 3
"""
        output_path = tmp_path / "complex.pdf"

        render_pdf(markdown, output_path)

        assert output_path.exists()
        # Complex document should be larger
        assert output_path.stat().st_size > 2000
