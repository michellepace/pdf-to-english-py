"""Render module for converting markdown to PDF."""

from typing import TYPE_CHECKING

from markdown_it import MarkdownIt
from weasyprint import HTML

if TYPE_CHECKING:
    from pathlib import Path

# Minimal CSS for readable PDF output
MINIMAL_CSS = """
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
                 "Helvetica Neue", Arial, sans-serif;
    line-height: 1.6;
    max-width: 210mm;
    margin: 20mm auto;
    padding: 0 15mm;
    color: #333;
}

h1, h2, h3, h4, h5, h6 {
    margin-top: 1.5em;
    margin-bottom: 0.5em;
    line-height: 1.3;
}

h1 { font-size: 2em; }
h2 { font-size: 1.5em; }
h3 { font-size: 1.25em; }

p {
    margin: 1em 0;
}

table {
    border-collapse: collapse;
    width: 100%;
    margin: 1em 0;
}

th, td {
    border: 1px solid #333;
    padding: 8px;
    text-align: left;
}

th {
    background-color: #f5f5f5;
    font-weight: bold;
}

img {
    max-width: 100%;
    height: auto;
}

ul, ol {
    margin: 1em 0;
    padding-left: 2em;
}

li {
    margin: 0.5em 0;
}

code {
    background-color: #f5f5f5;
    padding: 0.2em 0.4em;
    border-radius: 3px;
    font-family: monospace;
}

pre {
    background-color: #f5f5f5;
    padding: 1em;
    border-radius: 5px;
    overflow-x: auto;
}

pre code {
    background: none;
    padding: 0;
}
"""


def markdown_to_html(markdown: str) -> str:
    """Convert markdown to HTML, preserving embedded HTML content.

    Uses markdown-it-py which passes through HTML tags unchanged.

    Args:
        markdown: Markdown content with embedded HTML tables and base64 images.

    Returns:
        HTML body content (without document wrapper).
    """
    # Create markdown parser with HTML passthrough enabled
    md = MarkdownIt("commonmark", {"html": True})
    return md.render(markdown)


def wrap_with_styles(html_body: str) -> str:
    """Wrap HTML body with document structure and minimal CSS.

    Adds basic styling for:
    - Body fonts (sans-serif)
    - Table borders
    - Page margins
    - Image sizing

    Args:
        html_body: Raw HTML body content.

    Returns:
        Complete HTML document with <!DOCTYPE>, <html>, <head>, <style>, and <body>.
    """
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Translated Document</title>
    <style>
{MINIMAL_CSS}
    </style>
</head>
<body>
{html_body}
</body>
</html>
"""


def html_to_pdf(html: str, output_path: Path) -> Path:
    """Render HTML to PDF using WeasyPrint.

    Args:
        html: Complete HTML document with styles.
        output_path: Path where the PDF should be saved.

    Returns:
        Path to the generated PDF file.
    """
    html_doc = HTML(string=html)
    html_doc.write_pdf(output_path)
    return output_path


def render_pdf(markdown: str, output_path: Path) -> Path:
    """Full pipeline: markdown -> HTML -> PDF.

    Convenience function that combines all rendering steps.

    Args:
        markdown: Translated markdown with HTML tables and base64 images.
        output_path: Path for the output PDF.

    Returns:
        Path to the generated PDF file.
    """
    html_body = markdown_to_html(markdown)
    full_html = wrap_with_styles(html_body)
    return html_to_pdf(full_html, output_path)
