---
validated_against: All code as of commit a931d44
validated_by: uv run scripts/investigate_ocr.py input_pdfs/e2e_test.pdf
validated_date: 2026-01-27
---

# HANDOVER: PDF-to-English Translation Prototype

## What Was Built

A Python Gradio app that translates PDFs to English PDFs using Mistral AI.

```text
                    PIPELINE FLOW

┌──────────────┐
│     PDF      │  ← User uploads
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Base64      │  app.py encodes file
│  Encode      │
└──────┬───────┘
       │
       ▼
┌──────────────┐     ┌─────────────────────┐
│  Mistral     │────>│ Returns:            │
│  OCR API     │     │ • Markdown text     │
└──────────────┘     │ • HTML tables       │
       │             │ • Base64 images     │
       │             └─────────────────────┘
       ▼
┌──────────────┐
│  Inline      │  ocr.py replaces placeholders
│  Assets      │  with actual table/image data
└──────┬───────┘
       │
       ▼
┌──────────────┐     ┌─────────────────────┐
│  Mistral     │────>│ Returns:            │
│  Large API   │     │ • Translated MD     │
└──────────────┘     │ • Structure intact  │
       │             └─────────────────────┘
       ▼
┌──────────────┐
│ markdown-it  │  MD → HTML
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  WeasyPrint  │  HTML → PDF
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ English PDF  │  ← User downloads
└──────────────┘
```

Model Structure:

```text
src/pdf_to_english_py/
├── app.py          # Gradio UI + orchestration
├── ocr.py          # Mistral OCR extraction + asset inlining
├── translate.py    # Mistral Large translation
└── render.py       # markdown-it-py + WeasyPrint PDF generation

tests/
├── conftest.py       # Shared fixtures (input PDFs, Mistral client)
├── test_ocr.py
├── test_translate.py
├── test_render.py
├── test_app.py
└── test_e2e.py       # 1 integration test
```

---

## Q1: Where Does the PDF Go and How?

```text
┌────────────────────────┐
│     PDF JOURNEY        │
└────────────────────────┘

1. USER UPLOADS via Gradio
   │
   ▼
2. GRADIO saves to TEMP FILE
   Location: /tmp/gradio/xxxxx/filename.pdf
   │
   ▼
3. app.py handler() receives file path as string
   File: app.py → handler()
   │
   ▼
4. ocr.py encode_pdf_to_base64() reads file
   File: ocr.py → encode_pdf_to_base64()
   │
   ▼
5. BASE64 STRING sent to Mistral OCR API
   Format: "data:application/pdf;base64,{base64_pdf}"
   File: ocr.py → extract_pdf()
   │
   ▼
6. MISTRAL PROCESSES in cloud, returns JSON
   │
   ▼
7. OUTPUT PDF written to temp dir, then copied to /tmp/
   for Gradio download
   File: app.py → handler()
```

**Key code:**

```python
# ocr.py → extract_pdf()
base64_pdf = encode_pdf_to_base64(pdf_path)
ocr_response = client.ocr.process(
    model="mistral-ocr-latest",
    document={
        "type": "document_url",
        "document_url": f"data:application/pdf;base64,{base64_pdf}",
    },
    table_format="html",
    include_image_base64=True,
)
```

---

## Q2: How Do Images Work?

```text
┌──────────────────┐
│ IMAGE FLOW       │
└──────────────────┘

1. MISTRAL OCR extracts images from PDF
   Returns: Base64 data URI + bounding box
   │
   ▼
2. OCR RESPONSE contains placeholder in markdown:
   "![img-0.jpeg](img-0.jpeg)"

   Plus image data in separate array:
   images: [{ id: "img-0.jpeg", image_base64: "data:image/jpeg;base64,..." }]
   │
   ▼
3. ocr.py inline_images() REPLACES placeholder:
   "![img-0.jpeg](img-0.jpeg)"
        becomes
   "![img-0.jpeg](data:image/jpeg;base64,/9j/4AAQ...)"

   File: ocr.py → inline_images()
   (Tables inlined similarly via inline_tables() in ocr.py)
   │
   ▼
4. markdown-it-py CONVERTS to HTML:
   <img src="data:image/jpeg;base64,/9j/4AAQ..." alt="img-0.jpeg">
   │
   ▼
5. WeasyPrint EMBEDS base64 directly into PDF
   No external files needed - image data is inline
```

**Image formats supported:** JPEG, PNG (whatever Mistral OCR extracts)

**Key code:**

```python
# ocr.py → inline_images()
for image in images:
    image_id = image.get("id", "")
    image_base64 = image.get("image_base64", "")
    escaped_id = re.escape(image_id)
    pattern = rf"!\[{escaped_id}\]\({escaped_id}\)"
    replacement = f"![{image_id}]({image_base64})"
    result = re.sub(pattern, replacement, result)
```

---

## Q3: Translation Details

### 3A. Where is the LLM Call and Prompt?

**File:** `src/pdf_to_english_py/translate.py`

```python
response = client.chat.complete(
    model="mistral-large-latest",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": markdown},
    ],
)
```

### 3B. How Do We Protect Code From Translation?

**Current approach:** The prompt says "Do NOT translate URLs, file paths, or code"

**Reliability:** This is best-effort by the LLM. It usually works but isn't guaranteed.

**Token optimisation:** Before translation, `strip_images()` removes base64 image data (replacing with placeholders), then `restore_images()` re-inserts them after translation. This significantly reduces token usage. See `strip_images()` and `restore_images()` in translate.py.

**More robust options:**

1. Pre-process: Extract code blocks, replace with placeholders, translate, restore
2. Use markdown-it-py to parse and identify code blocks before translation
3. Add few-shot examples to the prompt showing code preservation

---

## Q4: Mistral OCR — Visual Alignment Analysis

This section documents what Mistral OCR provides that could improve visual alignment of translated PDFs. All outputs are single-column.

### 4A. What We Currently Use

| Data | Source | How Used | Code Location |
|------|--------|----------|---------------|
| `page.markdown` | OCR response | Main text content | `extract_pdf()` in ocr.py |
| `page.images[].id` | OCR response | Match placeholders | `extract_pdf()` in ocr.py |
| `page.images[].image_base64` | OCR response | Embed images inline | `extract_pdf()` in ocr.py |
| `page.tables[].id` | OCR response | Match placeholders | `extract_pdf()` in ocr.py |
| `page.tables[].content` | OCR response | Embed HTML tables | `extract_pdf()` in ocr.py |
| `table_format="html"` | API param | Get tables as HTML | `extract_pdf()` in ocr.py |
| `include_image_base64=True` | API param | Get base64 images | `extract_pdf()` in ocr.py |

**Current rendering (render.py):**

- A4 page (210mm × 297mm) with 10mm margins
- sans-serif font, no padding
- Images: hardcoded `width: 23.8%` (from prototype calculation, not dynamic)
- Tables: collapsed borders, no explicit width

### 4B. Available But Not Used — Visual Alignment Opportunities

| Data | Available From | Visual Alignment Potential |
|------|----------------|---------------------------|
| **Page dimensions** | `page.dimensions.dpi`, `.width`, `.height` | Calculate aspect ratio, set output page size |
| **Image bounding boxes** | `page.images[].top_left_x/y`, `.bottom_right_x/y` | Calculate image dimensions in pixels, set explicit width/height |
| **Hyperlinks** | `page.hyperlinks[]` | URLs only (no anchor text mapping) - cannot recreate clickable links |
| **Header content** | `page.header` (requires `extract_header=True`) | Separate header styling |
| **Footer content** | `page.footer` (requires `extract_footer=True`) | Separate footer styling |

### 4C. What Mistral OCR Does NOT Provide

These styling attributes cannot be extracted from the OCR response:

- ❌ Font family, size, weight
- ❌ Text colour
- ❌ Background colours
- ❌ Text positioning/coordinates (only images have bounding boxes)
- ❌ Line spacing
- ❌ Column layout info (though it handles multi-column input)
- ❌ Paragraph spacing

### 4D. Actionable Improvements

| Improvement | Effort | Impact | Implementation |
|-------------|--------|--------|----------------|
| **Set image dimensions from bbox** | Low | Images match original proportions | `extract_pdf()` must pass bbox to `inline_images()` (currently discarded in `extract_pdf()`), then add width/height to img tag |
| **Use page DPI for image sizing** | Medium | More accurate image scaling | Read `page.dimensions.dpi`, adjust image sizes accordingly |
| **Enable header/footer extraction** | Medium | Better document structure | Add `extract_header=True`, `extract_footer=True` to OCR call, style separately |

**Note:** Hyperlinks cannot be preserved - the API returns URLs without anchor text mapping.

### 4E. Investigation Script

Verify OCR response structure (outputs dimensions, bounding boxes, hyperlinks without base64 data):

```bash
uv run scripts/investigate_ocr.py input_pdfs/e2e_test.pdf
```

Sample Script Output:

<sample_script_output>

```json
{
  "model": "mistral-ocr-latest",
  "pages": [
    {
      "index": 0,
      "dimensions": {"dpi": 200, "width": 1654, "height": 2339},
      "hyperlinks": ["https://www.google.com/", "https://claude.ai/new"],
      "markdown_preview": "Sivu 1 / 2\n\n# Sujet général du document...",
      "markdown_length": 1808,
      "images": [{
        "id": "img-0.jpeg",
        "has_base64": true,
        "top_left_x": 152, "top_left_y": 1656,
        "bottom_right_x": 276, "bottom_right_y": 1779,
        "width_px": 124, "height_px": 123
      }],
      "tables_count": 2
    },
    {
      "index": 1,
      "dimensions": {"dpi": 200, "width": 1654, "height": 2339},
      "hyperlinks": ["https://www.google.com/"],
      "markdown_preview": "Sivu 2 / 2\n\n[tbl-2.html](tbl-2.html)...",
      "markdown_length": 1374,
      "images": [{
        "id": "img-1.jpeg",
        "has_base64": true,
        "top_left_x": 152, "top_left_y": 727,
        "bottom_right_x": 1058, "bottom_right_y": 912,
        "width_px": 906, "height_px": 185
      }],
      "tables_count": 1
    }
  ]
}
```

</sample_script_output>

Key observations:

- `model`: Model identifier returned by the API
- `dimensions`: Page size in pixels at given DPI (1654×2339 @ 200 DPI = A4)
- `hyperlinks`: URLs only, no anchor text mapping
- `markdown_preview`: Truncated preview of extracted markdown (full content in `markdown`)
- `markdown_length`: Character count of full markdown content
- `images`: Bounding box allows calculating pixel dimensions
- `tables_count`: Count only, no bounding box data for tables

---

## Files to Know

| File | Purpose |
|------|---------|
| `src/pdf_to_english_py/app.py` | Gradio UI, orchestrates pipeline |
| `src/pdf_to_english_py/ocr.py` | Mistral OCR, asset inlining |
| `src/pdf_to_english_py/translate.py` | Translation prompt + API call |
| `src/pdf_to_english_py/render.py` | Markdown→HTML→PDF, CSS styles |
| `tests/conftest.py` | Test fixtures |
| `.env` | API key (not committed) |
| `x_docs/SPEC.md` | Original requirements + hypothesis results |
| `x_docs/docs_mistral_ocr.md` | Mistral OCR API documentation |
| `scripts/investigate_ocr.py` | OCR response structure investigation |

---

## Hypothesis Test Results

| # | Hypothesis | Result |
|---|------------|--------|
| 1 | markdown-it-py preserves HTML tables | ✅ PASS |
| 2 | Translation preserves structure | ✅ PASS |
| 3 | Complex tables (colspan/rowspan) preserved | ✅ PASS |
| 4 | Base64 images render in PDF | ✅ PASS |
| 5 | Visual similarity to original | 🫤 To be improved |

---

## ⚠️ PROPOSED REFACTORS

### 1. Code Block Protection (LOW PRIORITY)

**Problem:** The prompt asks LLM not to translate code, but this is best-effort.

**Fix:** Pre-process markdown to extract code blocks, replace with placeholders, translate, restore (same pattern as images).
