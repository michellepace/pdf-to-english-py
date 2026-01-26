"""Profile the PDF translation pipeline, showing time spent in each stage.

Usage: uv run python scripts/pipeline_timing.py <pdf_path>
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path
from typing import TYPE_CHECKING, ParamSpec, TypeVar

from dotenv import load_dotenv
from mistralai import Mistral

if TYPE_CHECKING:
    from collections.abc import Callable

    from mistralai.models import OCRResponse

from pdf_to_english_py.ocr import (
    OcrPage,
    encode_pdf_to_base64,
    inline_images,
    inline_tables,
)
from pdf_to_english_py.render import render_pdf
from pdf_to_english_py.translate import translate_markdown

load_dotenv()

parser = argparse.ArgumentParser(description="Time PDF translation pipeline stages")
parser.add_argument("pdf_path", type=Path, help="Path to the PDF file to process")
args = parser.parse_args()

if not args.pdf_path.exists():
    print(f"ERROR: File not found: {args.pdf_path}")
    sys.exit(1)


P = ParamSpec("P")
T = TypeVar("T")


def timed(
    name: str,
) -> Callable[[Callable[P, T]], Callable[P, tuple[T, float]]]:
    """Decorator to time a function and return (result, elapsed_seconds)."""

    def decorator(func: Callable[P, T]) -> Callable[P, tuple[T, float]]:
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> tuple[T, float]:
            print(f"\n⏱️  Starting: {name}")
            start = time.time()
            result = func(*args, **kwargs)
            elapsed = time.time() - start
            print(f"✅ Completed: {name} in {elapsed:.2f}s")
            return result, elapsed

        return wrapper

    return decorator


@timed("1. Load PDF and encode to base64")
def step_encode(pdf_path: Path) -> str:
    """Load a PDF file and encode it to base64."""
    return encode_pdf_to_base64(pdf_path)


@timed("2. Mistral OCR API call")
def step_ocr(base64_pdf: str, client: Mistral) -> OCRResponse:
    """Call Mistral OCR API to extract text from PDF."""
    return client.ocr.process(
        model="mistral-ocr-latest",
        document={
            "type": "document_url",
            "document_url": f"data:application/pdf;base64,{base64_pdf}",
        },
        table_format="html",
        include_image_base64=True,
    )


@timed("3. Process OCR response (inline tables/images)")
def step_process(ocr_response: OCRResponse) -> str:
    """Process OCR response by inlining tables and images into markdown."""
    pages = []
    for page in ocr_response.pages:
        markdown = page.markdown
        if page.tables:
            tables_data = [{"id": t.id, "content": t.content} for t in page.tables]
            markdown = inline_tables(markdown, tables_data)
        if page.images:
            images_data = [
                {"id": img.id, "image_base64": img.image_base64} for img in page.images
            ]
            markdown = inline_images(markdown, images_data)
        pages.append(OcrPage(index=page.index, markdown=markdown))

    return "\n\n".join(p.markdown for p in pages)


@timed("4. Translation (Mistral Large)")
def step_translate(markdown: str, client: Mistral) -> str:
    """Translate markdown content using Mistral Large."""
    return translate_markdown(markdown, client)


@timed("5. Render to PDF (WeasyPrint)")
def step_render(markdown: str, output_path: Path) -> Path:
    """Render markdown to PDF using WeasyPrint."""
    return render_pdf(markdown, output_path)


def main() -> None:
    """Run the full PDF processing pipeline with timing for each step."""
    pdf_path = args.pdf_path
    output_path = Path(f"output_pdfs/{pdf_path.stem}_timed.pdf")
    output_path.parent.mkdir(exist_ok=True)

    print(f"📄 Processing: {pdf_path}")
    print(f"📏 File size: {pdf_path.stat().st_size / 1024:.1f} KB")

    client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])

    total_start = time.time()
    timings = {}

    # Step 1: Encode
    base64_pdf, timings["encode"] = step_encode(pdf_path)
    print(f"   Base64 length: {len(base64_pdf):,} chars")

    # Step 2: OCR
    ocr_response, timings["ocr"] = step_ocr(base64_pdf, client)
    print(f"   Pages: {len(ocr_response.pages)}")

    # Step 3: Process
    markdown, timings["process"] = step_process(ocr_response)
    print(f"   Markdown length: {len(markdown):,} chars")

    # Step 4: Translate
    translated, timings["translate"] = step_translate(markdown, client)
    print(f"   Translated length: {len(translated):,} chars")

    # Step 5: Render
    result_path, timings["render"] = step_render(translated, output_path)

    total_elapsed = time.time() - total_start

    print("\n" + "=" * 50)
    print("📊 TIMING SUMMARY")
    print("=" * 50)
    for step, elapsed in timings.items():
        pct = (elapsed / total_elapsed) * 100
        bar = "█" * int(pct / 2)
        print(f"{step:12} {elapsed:6.1f}s ({pct:4.1f}%) {bar}")
    print("-" * 50)
    print(f"{'TOTAL':12} {total_elapsed:6.1f}s")
    print(f"\n✅ Output: {result_path}")


if __name__ == "__main__":
    main()
