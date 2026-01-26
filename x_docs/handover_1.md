# HANDOVER: PDF-to-English Translation Prototype

## What Was Built

A Python Gradio app that translates French PDFs to English PDFs using Mistral AI.

```text
                    PIPELINE FLOW

┌──────────────┐
│  French PDF  │  ← User uploads
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
├── conftest.py     # Shared fixtures (sample PDFs, Mistral client)
├── test_ocr.py     # 13 tests (11 unit, 2 integration)
├── test_translate.py # 10 tests (3 unit, 7 integration)
├── test_render.py  # 15 unit tests
└── test_app.py     # 5 tests (2 unit, 3 integration)
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
   File: src/pdf_to_english_py/app.py:87-88
   │
   ▼
4. ocr.py encode_pdf_to_base64() reads file
   File: src/pdf_to_english_py/ocr.py:28-41
   │
   ▼
5. BASE64 STRING sent to Mistral OCR API
   Format: "data:application/pdf;base64,{base64_pdf}"
   File: src/pdf_to_english_py/ocr.py:110-118
   │
   ▼
6. MISTRAL PROCESSES in cloud, returns JSON
   │
   ▼
7. OUTPUT PDF written to temp dir, then copied to /tmp/
   for Gradio download
   File: src/pdf_to_english_py/app.py:109-112
```

**Key code:**

```python
# ocr.py:106-118
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

## Q2: Mistral OCR — Capabilities & What We're Using

### API Response Structure

```json
{
  "pages": [{
    "index": 0,
    "markdown": "# Title...",              // ✅ USING
    "dimensions": {"dpi": 200, "height": 2200, "width": 1700},  // ❌ NOT USING
    "images": [{
      "id": "img-0.jpeg",                  // ✅ Using
      "image_base64": "data:...",          // ✅ Using
      "top_left_x": 100,                   // ❌ NOT USING - bounding box
      "top_left_y": 200,
      "bottom_right_x": 500,
      "bottom_right_y": 400
    }],
    "tables": [{"id": "tbl-0.html", "content": "<table>..."}],  // ✅ USING
    "hyperlinks": ["https://..."],          // ❌ NOT USING*
    "header": null,                        // ❌ NOT ENABLED
    "footer": null                         // ❌ NOT ENABLED
  }],
  "model": "mistral-ocr-2512",
  "usage_info": {"pages_processed": 2, "doc_size_bytes": 150000}
}
```

### Feature Usage Table

| Feature | Available | We Use | How to Enable |
|---------|-----------|--------|---------------|
| Text extraction (markdown) | ✅ | ✅ | Default |
| Table extraction (HTML) | ✅ | ✅ | `table_format="html"` |
| Image extraction (base64) | ✅ | ✅ | `include_image_base64=True` |
| **Header extraction** | ✅ | ❌ | Add `extract_header=True` |
| **Footer extraction** | ✅ | ❌ | Add `extract_footer=True` |
| **Hyperlinks*** | ✅ | ❌ | Capture `page.hyperlinks` |
| **Image bounding boxes** | ✅ | ❌ | Use `top_left_x/y`, `bottom_right_x/y` |
| **Page dimensions** | ✅ | ❌ | Use `page.dimensions.dpi/height/width` |
| **Batch processing** | ✅ | ❌ | Use Batch API (50% cheaper) |
| **Cloud file upload** | ✅ | ❌ | Use `client.files.upload()` instead of base64 |

*`hyperlinks` captures PDF hyperlink annotations only, not URL text.

### What's MISSING for Style Matching

❌ Font family, size, weight
❌ Text colour
❌ Background colours
❌ Text positioning (images have bounding boxes, but text coordinates not provided)
❌ Line spacing
❌ Column layout info

### What's AVAILABLE

✅ Page dimensions (dpi, height, width)
✅ Image bounding boxes (x, y coordinates)
✅ Semantic structure (headers, paragraphs, lists)
✅ Table structure with colspan/rowspan

### Potential Improvements

| Approach | Effort | Result |
|----------|--------|--------|
| **Better CSS in render.py** | Low | Nicer default typography, won't match original |
| **Use page dimensions for margins** | Medium | Approximate original proportions |
| **Position images using bbox** | Medium | Images in roughly correct positions |
| **Extract styles with separate tool (e.g., pdfplumber)** | High | Could extract fonts/colours from original |
| **Two-column detection** | High | Detect multi-column layout, render accordingly |
| **Preserve hyperlinks** | Low | Pass links through to output document |
| **Header/footer handling** | Medium | Extract separately to maintain document structure |
| **Batch API for scale** | Medium | 50% cost reduction when processing multiple documents |

**Current CSS is in:** `src/pdf_to_english_py/render.py:9-83`

---

## Q3: How Do Images Work?

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              IMAGE FLOW                                          │
└─────────────────────────────────────────────────────────────────────────────────┘

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

   File: src/pdf_to_english_py/ocr.py:67-90
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
# ocr.py:80-89
for image in images:
    image_id = image.get("id", "")
    image_base64 = image.get("image_base64", "")
    escaped_id = re.escape(image_id)
    pattern = rf"!\[{escaped_id}\]\({escaped_id}\)"
    replacement = f"![{image_id}]({image_base64})"
    result = re.sub(pattern, replacement, result)
```

---

## Q4: Translation Details

### Where is the LLM Call?

**File:** `src/pdf_to_english_py/translate.py:66-72`

```python
response = client.chat.complete(
    model="mistral-large-latest",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": markdown},
    ],
)
```

Translation Prompt: `src/pdf_to_english_py/translate.py:5-36`

### What Happens If Document Is Already English?

**Current behaviour:** The LLM will still process it. It may:

- Return the text mostly unchanged
- Make minor "improvements" or rephrasings
- Cost API tokens unnecessarily

**Possible fix:** Add language detection before translation.

### Can We Support German (or Other Languages)?

**Yes, easily.** The function signature already supports it:

```python
def translate_markdown(
    markdown: str,
    client: Mistral,
    source_lang: str = "French",   # ← Change this
    target_lang: str = "English",  # ← Or this
) -> str:
```

**To add German→English:** Just call with `source_lang="German"`

**To expose in UI:** Add a dropdown in `app.py` for source language selection.

### How Do We Protect Code From Translation?

**Current approach:** The prompt says "Do NOT translate URLs, file paths, or code"

**Reliability:** This is best-effort by the LLM. It usually works but isn't guaranteed.

**More robust options:**

1. Pre-process: Extract code blocks, replace with placeholders, translate, restore
2. Use markdown-it-py to parse and identify code blocks before translation
3. Add few-shot examples to the prompt showing code preservation

---

## Running the App

```bash
# Install dependencies
uv sync

# Set API key
echo "MISTRAL_API_KEY=your_key" > .env

# Run app
uv run python -m pdf_to_english_py.app
# Opens at http://127.0.0.1:7860

# Run tests
uv run pytest -v                      # All tests
uv run pytest -v -k "not integration" # Unit tests only (no API)
uv run pytest -v -m integration       # Integration tests (needs API key)
```

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

---

## Hypothesis Test Results

| # | Hypothesis | Result |
|---|------------|--------|
| 1 | markdown-it-py preserves HTML tables | ✅ PASS |
| 2 | Translation preserves structure | ✅ PASS |
| 3 | Complex tables (colspan/rowspan) preserved | ✅ PASS |
| 4 | Base64 images render in PDF | ✅ PASS |
| 5 | Visual similarity to original | ⏳ Manual verification |

---

## ⚠️ PROPOSED REFACTORS

### 1. Code Block Protection (LOW PRIORITY)

**Problem:** The prompt asks LLM not to translate code, but this is best-effort.

**Fix:** Pre-process markdown to extract code blocks, replace with placeholders, translate, restore (same pattern as images).
