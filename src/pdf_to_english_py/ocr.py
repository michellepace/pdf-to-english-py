"""OCR extraction module using Mistral OCR 3."""

import base64
import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pathlib import Path

    from mistralai import Mistral


@dataclass
class PageDimensions:
    """Page dimensions in millimetres, calculated from OCR pixel data."""

    width_mm: float
    height_mm: float

    @classmethod
    def from_ocr(cls, width_px: int, height_px: int, dpi: int) -> PageDimensions:
        """Create PageDimensions from OCR pixel dimensions."""
        return cls(
            width_mm=round((width_px / dpi) * 25.4, 1),
            height_mm=round((height_px / dpi) * 25.4, 1),
        )


@dataclass
class ImageMetadata:
    """Metadata for an image extracted from OCR, including sizing info."""

    image_id: str
    width_percent: float

    @classmethod
    def from_bounding_box(
        cls,
        image_id: str,
        top_left_x: int,
        bottom_right_x: int,
        page_width: int,
    ) -> ImageMetadata:
        """Create ImageMetadata from bounding box coordinates.

        Args:
            image_id: The image identifier (e.g. "img-0.jpeg").
            top_left_x: X coordinate of top-left corner.
            bottom_right_x: X coordinate of bottom-right corner.
            page_width: Width of the page in pixels.

        Returns:
            ImageMetadata with calculated width_percent.
        """
        width_px = bottom_right_x - top_left_x
        width_percent = (width_px / page_width) * 100
        return cls(image_id=image_id, width_percent=round(width_percent, 1))


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
    images: list[ImageMetadata] = field(default_factory=list)
    page_dimensions: PageDimensions | None = None


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
    all_images: list[ImageMetadata] = []
    page_dimensions: PageDimensions | None = None

    for page in ocr_response.pages:
        # Capture page dimensions from first page
        if page_dimensions is None and page.dimensions:
            page_dimensions = PageDimensions.from_ocr(
                width_px=page.dimensions.width,
                height_px=page.dimensions.height,
                dpi=page.dimensions.dpi,
            )
        # Start with the raw markdown
        markdown = page.markdown

        # Inline tables if present
        if page.tables:
            tables_data = [{"id": t.id, "content": t.content} for t in page.tables]
            markdown = inline_tables(markdown, tables_data)

        # Inline images if present and capture metadata
        if page.images:
            images_data = [
                {"id": img.id, "image_base64": img.image_base64} for img in page.images
            ]
            markdown = inline_images(markdown, images_data)

            # Capture image metadata from bounding boxes (requires page dimensions)
            if page.dimensions:
                for img in page.images:
                    if img.top_left_x is None or img.bottom_right_x is None:
                        continue
                    metadata = ImageMetadata.from_bounding_box(
                        image_id=img.id,
                        top_left_x=img.top_left_x,
                        bottom_right_x=img.bottom_right_x,
                        page_width=page.dimensions.width,
                    )
                    all_images.append(metadata)

        pages.append(OcrPage(index=page.index, markdown=markdown))

    # Combine all pages into raw_markdown
    raw_markdown = "\n\n".join(page.markdown for page in pages)

    return OcrResult(
        pages=pages,
        raw_markdown=raw_markdown,
        images=all_images,
        page_dimensions=page_dimensions,
    )
