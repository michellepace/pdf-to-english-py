"""OCR extraction module using Mistral OCR 3."""

import base64
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pathlib import Path

    from mistralai import Mistral


@dataclass
class OcrPage:
    """Represents a single page of OCR output with inlined assets."""

    index: int
    markdown: str  # Markdown with tables/images inlined


@dataclass
class OcrResult:
    """Complete OCR result for a document."""

    pages: list[OcrPage]
    raw_markdown: str  # Combined markdown from all pages


def encode_pdf_to_base64(pdf_path: Path) -> str:
    """Encode a local PDF file to base64 string.

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        Base64-encoded string of the PDF content.

    Raises:
        FileNotFoundError: If the PDF file doesn't exist.
    """
    with pdf_path.open("rb") as pdf_file:
        return base64.b64encode(pdf_file.read()).decode("utf-8")


def inline_tables(markdown: str, tables: list[dict[str, Any]]) -> str:
    """Replace table placeholders with actual HTML table content.

    Replaces patterns like [tbl-0.html](tbl-0.html) with the HTML from
    the tables array.

    Args:
        markdown: Raw markdown from OCR with table placeholders.
        tables: List of table objects with 'id' and 'content' fields.

    Returns:
        Markdown with table placeholders replaced by actual HTML.
    """
    result = markdown
    for table in tables:
        table_id = table.get("id", "")
        table_content = table.get("content", "")
        # Replace the link-style placeholder: [tbl-N.html](tbl-N.html)
        placeholder = f"[{table_id}]({table_id})"
        result = result.replace(placeholder, table_content)
    return result


def inline_images(markdown: str, images: list[dict[str, Any]]) -> str:
    """Replace image placeholders with base64 data URIs.

    Replaces patterns like ![img-0.jpeg](img-0.jpeg) with
    ![img-0.jpeg](data:image/jpeg;base64,...).

    Args:
        markdown: Markdown with image placeholders.
        images: List of image objects with 'id' and 'image_base64' fields.

    Returns:
        Markdown with image placeholders replaced by base64 data URIs.
    """
    result = markdown
    for image in images:
        image_id = image.get("id", "")
        image_base64 = image.get("image_base64", "")
        # Replace the image-style placeholder: ![img-N.jpeg](img-N.jpeg)
        # Need to escape special regex characters in the image_id
        escaped_id = re.escape(image_id)
        pattern = rf"!\[{escaped_id}\]\({escaped_id}\)"
        replacement = f"![{image_id}]({image_base64})"
        result = re.sub(pattern, replacement, result)
    return result


def extract_pdf(pdf_path: Path, client: Mistral) -> OcrResult:
    """Extract text, tables, and images from a PDF using Mistral OCR 3.

    Uses table_format="html" and include_image_base64=True.
    Automatically inlines tables and images into the markdown.

    Args:
        pdf_path: Path to the PDF file.
        client: Mistral API client.

    Returns:
        OcrResult with inlined markdown content.
    """
    # Encode PDF to base64 for upload
    base64_pdf = encode_pdf_to_base64(pdf_path)

    # Call Mistral OCR
    ocr_response = client.ocr.process(
        model="mistral-ocr-latest",
        document={
            "type": "document_url",
            "document_url": f"data:application/pdf;base64,{base64_pdf}",
        },
        table_format="html",
        include_image_base64=True,
    )

    # Process each page
    pages: list[OcrPage] = []
    for page in ocr_response.pages:
        # Start with the raw markdown
        markdown = page.markdown

        # Inline tables if present
        if page.tables:
            tables_data = [{"id": t.id, "content": t.content} for t in page.tables]
            markdown = inline_tables(markdown, tables_data)

        # Inline images if present
        if page.images:
            images_data = [
                {"id": img.id, "image_base64": img.image_base64} for img in page.images
            ]
            markdown = inline_images(markdown, images_data)

        pages.append(OcrPage(index=page.index, markdown=markdown))

    # Combine all pages into raw_markdown
    raw_markdown = "\n\n".join(page.markdown for page in pages)

    return OcrResult(pages=pages, raw_markdown=raw_markdown)
