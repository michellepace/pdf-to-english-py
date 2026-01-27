#!/usr/bin/env python
"""Translate a PDF to English.

Usage: uv run scripts/translate_pdf.py <input.pdf>
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from mistralai import Mistral

from pdf_to_english_py.ocr import extract_pdf
from pdf_to_english_py.render import render_pdf
from pdf_to_english_py.translate import translate_markdown

load_dotenv()

input_path = Path(sys.argv[1])
output_dir = Path("output_pdfs")
output_dir.mkdir(exist_ok=True)
output_path = output_dir / f"{input_path.stem}_EN.pdf"
client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])

print("Extracting...")
ocr_result = extract_pdf(input_path, client)

print("Translating...")
translated_md = translate_markdown(ocr_result.raw_markdown, client)

print("Rendering...")
render_pdf(translated_md, output_path)

print(f"Done: {output_path}")
