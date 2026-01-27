## OBJECTIVE

Visually align the output PDF using data returned from the Mistral OCR API so it looks more similar to the input PDF. The PDF pipeline is in @x_docs/handover_1.md

## Success Criteria (in scope)

For Output PDF:

1. [ ] Same page size (width, height)
2. [ ] Same image size (width, height)

## Out of scope / Deferred

- ~~Hyperlinks~~ — Not possible, Mistral OCR doesn't embed URLs in markdown (see Appendix)
- Margins — Can only be inferred if content touches edges; use sensible defaults
- Headers/footers — Requires `extract_header=True` flag, test separately

## Non-functional requirements

- TDD (pragmatic) small purpose driven tests
- For tests that hit API mark with "integration"
- Add tests to appropriate test files (`test_ocr.py`, `test_render.py`, `test_e2e.py`)

## References

- Mistral OCR 3 features: `x_docs/docs_mistral_ocr.md`
- Mistral OCR 3 API (detailed with code examples): `x_docs/docs_mistral_ocr.md`
- Current CSS is in: `src/pdf_to_english_py/render.py`

## Investigate

Visual Analysis (current state):

- Input PDF `sample_pdfs/e2e_test.pdf`
- Output PDF `output_pdfs/e2e_test_EN.pdf` (fails both success criteria)

Metadata structure of what Mistral OCR actually returns

- Run `uv run scripts/investigate_ocr.py sample_pdfs/e2e_test.pdf`

## Important Notes

1. 🔥 **Do NOT send base64 images to the translation LLM** — The `strip_images()` function in `translate.py` removes base64 data **before** translation. Do NOT modify images during OCR extraction or translation steps.

2. ⚠️ **Images MUST remain in markdown format** — The `strip_images()` function uses this regex:

   ```python
   pattern = r"!\[([^\]]*)\]\((data:image/[^)]+)\)"
   ```

   This ONLY matches markdown format `![alt](data:image/...)`. If you convert images to HTML `<img>` tags during OCR or translation, `strip_images()` will NOT match them and megabytes of base64 data will be sent to the translation API.

3. **Extend OcrResult to carry metadata** — Currently `OcrResult` only contains `pages` and `raw_markdown`. It needs to also carry:
   - Page dimensions (dpi, width, height) per page
   - Image bounding boxes (for calculating proportional sizes)

4. **Apply image sizing in render.py via CSS** — The pipeline with metadata flow:

   ```
   OCR (capture metadata) → translate (strip/restore images) → render (use metadata)
                       ↓                                              ↑
                    OcrResult ─────────── dimensions, bbox ──────────→
   ```

   Apply sizing in `render.py` using CSS/WeasyPrint `@page` rules and image width styles. Do NOT modify the markdown format during OCR extraction.

5. **Calculate image width as percentage of page width**:

   ```
   image_width_px = bottom_right_x - top_left_x
   image_width_percent = (image_width_px / page_width) * 100
   ```

6. We are visually aligning output PDF based on what is available via Mistral OCR API.

**ASK ME QUESTIONS TO CONFIRM / CLARIFY UNDERSTANDING**

---

## Experiment: CSS-Based Sizing (Validated)

**Approach tested:** Apply sizing via CSS in `render.py` using `@page` rules and `img` width styles.

**Results on `e2e_test.pdf`:**

| Metric | Source | No CSS | With CSS | Status |
|--------|--------|--------|----------|--------|
| Page size | 210×297mm | 210×297mm | 210×297mm | ✅ |
| Page count | 2 | 3 | 2 | ✅ Fixed |
| Image width | ~50mm (23.8% of page) | ~139mm (overflow!) | ~45mm | ✅ Close |

**Working CSS template:**

```css
/* Page size from OCR: pixels / dpi * 25.4 = mm */
@page {
    size: 210mm 297mm;  /* from dimensions.width/height */
    margin: 10mm;
}

body {
    font-family: sans-serif;
    margin: 0;
    padding: 0;
}

/* Target each image by its OCR ID (preserved in alt attribute) */
img[alt="img-0.jpeg"] { width: 54.8%; height: auto; }
img[alt="img-1.jpeg"] { width: 54.8%; height: auto; }
img[alt="img-2.jpeg"] { width: 7.5%; height: auto; }
/* ... one rule per image */
```

**Why this works for multiple images:**

- OCR returns images with IDs like `img-0.jpeg`, `img-1.jpeg`
- The `alt` attribute survives the entire pipeline: OCR → translate → render
- CSS attribute selectors `img[alt="..."]` target specific images
- Each image gets its own calculated width

**Note:** Dynamic image sizing is now implemented. The `render_pdf()` function accepts `images` metadata from OCR and generates CSS rules automatically via `generate_image_css()`.

---

## Appendix: Mistral OCR Response Structure

The Mistral OCR API returns JSON (Python SDK parses into objects):

```json
{
  "pages": [
    {
      "index": 0,
      "markdown": "# Title\n\nText with **bold**...\n\n[tbl-0.html](tbl-0.html)",
      "dimensions": {"dpi": 200, "width": 1654, "height": 2339},
      "hyperlinks": ["https://www.google.com/", "https://claude.ai/new"],
      "images": [],
      "tables": [{"id": "tbl-0.html", "content": "<table>...</table>", "format": "html"}],
      "header": null,
      "footer": null
    },
    {
      "index": 1,
      "markdown": "[tbl-2.html](tbl-2.html)\n\n![img-0.jpeg](img-0.jpeg)\n\n![img-1.jpeg](img-1.jpeg)\n\n![img-2.jpeg](img-2.jpeg)",
      "dimensions": {"dpi": 200, "width": 1654, "height": 2339},
      "hyperlinks": ["https://www.google.com/"],
      "images": [
        {"id": "img-0.jpeg", "top_left_x": 152, "top_left_y": 813, "bottom_right_x": 1058, "bottom_right_y": 1001, "image_base64": "..."},
        {"id": "img-1.jpeg", "top_left_x": 152, "top_left_y": 1178, "bottom_right_x": 1058, "bottom_right_y": 1368, "image_base64": "..."},
        {"id": "img-2.jpeg", "top_left_x": 152, "top_left_y": 1546, "bottom_right_x": 276, "bottom_right_y": 1672, "image_base64": "..."}
      ],
      "tables": [{"id": "tbl-2.html", "content": "<table>...</table>", "format": "html"}],
      "header": null,
      "footer": null
    }
  ],
  "model": "mistral-ocr-latest",
  "usage_info": {"pages_processed": 2, "doc_size_bytes": 107000}
}
```

### Key findings for `e2e_test.pdf`

| Field | Value | Notes |
|-------|-------|-------|
| `dimensions.dpi` | 200 | |
| `dimensions.width` | 1654 px | ≈ 210mm (A4) at 200 DPI |
| `dimensions.height` | 2339 px | ≈ 297mm (A4) at 200 DPI |
| `hyperlinks` (page 1) | `["https://www.google.com/", "https://claude.ai/new"]` | URLs detected but NOT embedded in markdown |
| `hyperlinks` (page 2) | `["https://www.google.com/"]` | |
| `img-0.jpeg` bounding box | (152, 813) to (1058, 1001) | Width: 906px = 54.8% |
| `img-1.jpeg` bounding box | (152, 1178) to (1058, 1368) | Width: 906px = 54.8% |
| `img-2.jpeg` bounding box | (152, 1546) to (276, 1672) | Width: 124px = 7.5% |

### Limitations discovered

- **Hyperlinks**: The `hyperlinks` array contains URLs, but they are **not formatted as markdown links** in the `markdown` field. The text "Google Link" appears as bold text, not `[Google Link](url)`.
