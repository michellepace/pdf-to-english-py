"""Render module for converting markdown to PDF."""

from pathlib import Path
from typing import TYPE_CHECKING

from markdown_it import MarkdownIt
from weasyprint import HTML

if TYPE_CHECKING:
    from pdf_to_english_py.ocr import ImageMetadata, PageDimensions

# Bundled font for consistent rendering across environments
PROJECT_ROOT = Path(__file__).resolve().parents[2]
FONT_PATH = PROJECT_ROOT / "fonts" / "AtkinsonHyperlegibleNextVF-Variable.ttf"
FONT_URL = FONT_PATH.as_uri()

BASE_CSS = f"""
@font-face {{
    font-family: "Atkinson Hyperlegible";
    src: url("{FONT_URL}") format("truetype");
    font-weight: 100 900;
    font-style: normal;
}}

body {{
    font-family: "Atkinson Hyperlegible", sans-serif;
    color: #222;
    line-height: 1.1;
    margin: 0;
    padding: 0;
}}

table {{
    border-collapse: collapse;
}}

th, td {{
    border: 1px solid #333;
    padding: 4px;
}}
"""

DEFAULT_PAGE_SIZE = (210.0, 297.0)  # A4 in mm


def generate_page_css(page_dimensions: PageDimensions | None) -> str:
    """Generate @page CSS rule from page dimensions.

    Args:
        page_dimensions: Page dimensions from OCR, or None for A4 default.

    Returns:
        CSS @page rule with size and margin.
    """
    if page_dimensions:
        width, height = page_dimensions.width_mm, page_dimensions.height_mm
    else:
        width, height = DEFAULT_PAGE_SIZE

    return f"@page {{ size: {width}mm {height}mm; margin: 10mm; }}"


def generate_image_css(images: list[ImageMetadata]) -> str:
    """Generate CSS rules for image sizing based on OCR metadata.

    Uses CSS attribute selectors to target images by their alt text,
    which is preserved from the OCR image ID through the pipeline.

    Args:
        images: List of ImageMetadata with sizing information.

    Returns:
        CSS rules for image sizing, or empty string if no images.
    """
    if not images:
        return ""

    rules = []
    for img in images:
        # Escape quotes in image ID for CSS attribute selector
        safe_id = img.image_id.replace('"', '\\"')
        rules.append(
            f'img[alt="{safe_id}"] {{ width: {img.width_percent}%; height: auto; }}'
        )

    return "\n".join(rules)


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


def wrap_with_styles(
    html_body: str,
    images: list[ImageMetadata] | None = None,
    page_dimensions: PageDimensions | None = None,
) -> str:
    """Wrap HTML body with document structure and styling.

    Adds basic styling for:
    - Atkinson Hyperlegible font (bundled)
    - Table borders
    - Page size and margins (from OCR or A4 default)
    - Dynamic image sizing (if metadata provided)

    Args:
        html_body: Raw HTML body content.
        images: Optional image metadata for dynamic sizing.
        page_dimensions: Optional page dimensions from OCR.

    Returns:
        Complete HTML document with <!DOCTYPE>, <html>, <head>, <style>, and <body>.
    """
    page_css = generate_page_css(page_dimensions)
    image_css = generate_image_css(images or [])
    all_css = BASE_CSS + "\n" + page_css + ("\n" + image_css if image_css else "")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Translated Document</title>
    <style>
{all_css}
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


def render_pdf(
    markdown: str,
    output_path: Path,
    images: list[ImageMetadata] | None = None,
    page_dimensions: PageDimensions | None = None,
) -> Path:
    """Full pipeline: markdown -> HTML -> PDF.

    Convenience function that combines all rendering steps.

    Args:
        markdown: Translated markdown with HTML tables and base64 images.
        output_path: Path for the output PDF.
        images: Optional image metadata for dynamic sizing.
        page_dimensions: Optional page dimensions from OCR.

    Returns:
        Path to the generated PDF file.
    """
    html_body = markdown_to_html(markdown)
    full_html = wrap_with_styles(
        html_body, images=images, page_dimensions=page_dimensions
    )
    return html_to_pdf(full_html, output_path)
