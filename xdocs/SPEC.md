# Build A PDF-to-English Prototype

## Objective

Build a Python `Gradio` prototype app as a `uv` project:

- **Input:** User uploads a PDF
- **Output:** User downloads a translated English PDF

**Pipeline:**

1. Extract text from PDF using `Mistral OCR 3` (with `table_format="html"`)
2. Translate extracted text to English using `mistral-large-latest`
3. Convert markdown to HTML using `markdown-it-py`
4. Render translation as downloadable PDF using `WeasyPrint`

**Success criteria:** All 5 hypotheses tested with pass/fail recorded in the Result column below.

This prototype informs the Next.js implementation at [pdf-to-english](https://github.com/michellepace/pdf-to-english).

---

## Pipeline Diagram

```text
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│     PDF     │ ──> │ Mistral OCR │ ──> │  Translate  │ ──> │  Convert    │ ──> │ English PDF │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
       ↑             markdown+HTML      Mistral Large       markdown-it-py       WeasyPrint  ↓
       ↑                                                                                     ↓
  User Upload                                                                        User Download
```

**OCR output format (hybrid):**

- **Text content:** Markdown (headers, paragraphs, bold, lists)
- **Tables:** HTML with colspan/rowspan (when using `table_format="html"`)
- **Images:** Base64 data, referenced via markdown placeholders `![img-0.jpeg](img-0.jpeg)`

---

## Hypotheses to Test

| # | Hypothesis | Question | Result |
| --- | ------------ | ---------- | -------- |
| 1 | Markdown conversion | Does `markdown-it-py` correctly convert OCR output while preserving embedded HTML tables? | ✅ PASS |
| 2 | Translation preserves structure | Does Mistral Large preserve HTML tags and markdown formatting? | ✅ PASS |
| 3 | Table fidelity | Are complex tables (merged cells, nested headers) preserved through the pipeline? | ✅ PASS |
| 4 | Image embedding | Do base64-embedded images render correctly in the final PDF? | ✅ PASS |
| 5 | Visual similarity | Is the output PDF visually similar in structure to the input? | 🫤 To be improved |

**Test files:**

| File | Tests | Contains |
| ------ | ------- | ---------- |
| `input_pdfs/french-tables.pdf` | 1, 2, 3, 5 | Complex tables |
| `input_pdfs/newsletter-images.pdf` | 1, 2, 4, 5 | Embedded images |

---

## Reference Materials

### 1. Mistral OCR API

Contains all OCR patterns needed: API calls, file upload, signed URLs, output structure, placeholder formats:
- https://docs.mistral.ai/studio-api/document-processing/overview.md
- https://docs.mistral.ai/studio-api/document-processing/basic_ocr.md

Irrelevant to this project, included for completeness:
- https://docs.mistral.ai/studio-api/document-processing/annotations.md
- https://docs.mistral.ai/studio-api/document-processing/document_qna.md

### 2. Gradio UI Pattern

Mistal guide for gradio: https://github.com/mistralai/cookbook/blob/main/third_party/gradio/MistralOCR.md

Gradio docs (markdown can be copied):
- https://gradio.app/guides/quickstart
- https://gradio.app/guides/themes
- https://gradio.app/guides/four-kinds-of-interfaces

### 3. Libraries

| Library | Purpose | Why chosen |
| --------- | --------- | ------------ |
| `markdown-it-py` | Convert markdown → HTML | Passes through embedded HTML unchanged |
| `WeasyPrint` | Render HTML → PDF | Supports `colspan`/`rowspan` in tables |

**Note:** `markdown-pdf` was rejected — its PyMuPDF backend doesn't support merged table cells.

---

## Notes

1. Store `MISTRAL_API_KEY` in `.env` (not committed).
2. This is an unsolved problem — no existing Mistral OCR → PDF solutions exist. This prototype is exploratory.
3. Deployment options in [deploy_railway.md](deploy_railway.md) (for later, once prototype works locally).
4. Other references I want to keep: <https://huggingface.co/spaces/merterbak/Mistral-OCR> and <https://www.datacamp.com/tutorial/mistral-ocr-3-full-guide>
