"""Investigate Mistral OCR response structure for a PDF.

Calls Mistral OCR API and prints the metadata structure (dimensions,
hyperlinks, image bounding boxes) without the large base64 image data.
Useful for understanding what data is available for visual alignment.

Usage: uv run scripts/investigate_ocr.py <input.pdf>
"""

import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from mistralai import Mistral

from pdf_to_english_py.ocr import encode_pdf_to_base64

load_dotenv()

input_path = Path(sys.argv[1])
client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])

print(f"Processing: {input_path}")

# Encode PDF and call OCR
base64_pdf = encode_pdf_to_base64(input_path)

ocr_response = client.ocr.process(
    model="mistral-ocr-latest",
    document={
        "type": "document_url",
        "document_url": f"data:application/pdf;base64,{base64_pdf}",
    },
    table_format="html",
    include_image_base64=True,
)

# Extract relevant data (excluding large base64 strings)
output: dict[str, object] = {
    "model": ocr_response.model,
    "pages": [],
}

for page in ocr_response.pages:
    page_data: dict[str, object] = {
        "index": page.index,
        "dimensions": {
            "dpi": page.dimensions.dpi,
            "width": page.dimensions.width,
            "height": page.dimensions.height,
        }
        if page.dimensions
        else None,
        "hyperlinks": list(page.hyperlinks) if page.hyperlinks else [],
        "markdown_preview": page.markdown[:500] if page.markdown else None,
        "markdown_length": len(page.markdown) if page.markdown else 0,
        "images": [],
        "tables_count": len(page.tables) if page.tables else 0,
    }

    # Extract image metadata (bounding boxes, not base64 data)
    if page.images:
        for img in page.images:
            img_data: dict[str, object] = {
                "id": img.id,
                "has_base64": bool(img.image_base64),
                "top_left_x": img.top_left_x,
                "top_left_y": img.top_left_y,
                "bottom_right_x": img.bottom_right_x,
                "bottom_right_y": img.bottom_right_y,
            }
            # Calculate dimensions from bounding box
            if img.top_left_x is not None and img.bottom_right_x is not None:
                img_data["width_px"] = img.bottom_right_x - img.top_left_x
            if img.top_left_y is not None and img.bottom_right_y is not None:
                img_data["height_px"] = img.bottom_right_y - img.top_left_y
            page_data["images"].append(img_data)  # type: ignore[union-attr]

    output["pages"].append(page_data)  # type: ignore[union-attr]

print(json.dumps(output, indent=2))
