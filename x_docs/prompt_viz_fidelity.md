# Instruction: Improve PDF Visual Fidelity Using Available OCR Data

## Goal

Modify the codebase so that generated PDFs look as similar as possible to the original input PDFs, by using OCR metadata fields we currently ignore.

---

## Context

This project uses Mistral OCR 3 to extract text from PDFs, translate it, and render new PDFs. Currently, we only use basic text/image/table content and ignore metadata that could improve visual fidelity.

---

## Analysis

You need to compare:

1. x_docs/docs_mistral_ocr.md (API documentation - authoritative schema with explanations) → What's available
2. src/pdf_to_english_py/ocr.py → What we capture
3. src/pdf_to_english_py/render.py → What we use

## Determine What to Change

For each discrepency of "What's available" vs "What we use" determine if we did use it, would it bring us closer to visual aligment of the original uploaded PDF?

For that which you determine would be advantages to use, consider these potential files for modification (TDD)

- `tests/test_ocr.py`
- `src/pdf_to_english_py/ocr.py`
- `tests/test_render.py`
- `src/pdf_to_english_py/render.py`

---

## Verification

After changes:

1. Run `uv run pytest` — all tests pass
2. Run the full pipeline on `input_pdfs/cv.pdf`
3. Compare output PDF dimensions to original
4. Verify images are positioned closer to original locations

---

## What's NOT Possible (API Limitations)

The OCR API does NOT provide:

- Font family, size, weight
- Text colour or background colours
- Text positioning (only images have coordinates)
- Line spacing or column layout detection

These would require additional tools (e.g., pdfplumber) or computer vision.
