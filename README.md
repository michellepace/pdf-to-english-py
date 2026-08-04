# Prototype: PDF to English

A quick spike to explore Mistral OCR: a Python Gradio app where you upload a PDF and download it translated into British English.

<div align="center">
  <img src="images/ocr_form.jpg" alt="Mistral OCR form understanding: scanned historical form on the left, extracted structured text on the right with PDF and Markdown output tabs. 2169 characters extracted from a single page." width="500">
  <p><em>Mistral OCR extracting from a scanned PDF</em></p>
</div>

<div align="center">
  <a href="https://pdf-to-english-prototype.up.railway.app/">
    <img src="images/app_screenshot.jpg" alt="Dark-themed Gradio interface with Upload PDF drop zone on the left, Download English PDF output (formulaire_médical_english.pdf, 51.3 KB) on the right, completed progress steps: Extracting text (OCR), Translating to English, Rendering PDF, Translation complete. Below: Mistral Key input field with 'Get one free' link, and a copper-coloured Convert To English button." width="500">
  </a>
  <p><em>Upload a PDF to translate to English (click image)</em></p>
</div>

The UI is simple, modelled on this [HTML mock-up](https://michellepace.github.io/pdf-to-english-py/mock-up/prototype.html). For examples, see [`input_pdfs/`](input_pdfs/) and their translations in [`output_pdfs/`](output_pdfs/).

## 🔄 PDF Pipeline Flow

```text
                    PIPELINE FLOW

┌──────────────┐
│     PDF      │  ← 🙂 User uploads
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Base64      │  ocr.py encodes file
│  Encode      │
└──────┬───────┘
       │
       ▼
┌──────────────┐     ┌─────────────────────┐ 🤖
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
┌──────────────┐     ┌─────────────────────┐ 🤖
│  Mistral Lge │────>│ Returns:            │
│  LLM API     │     │ • Translated MD     │
└──────────────┘     │ • Structure intact  │
       │             └─────────────────────┘
       │  (images stripped before, restored after)
       ▼
┌──────────────┐
│ markdown-it  │  MD → HTML                  🔧
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  WeasyPrint  │  HTML → PDF                 🔧
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ English PDF  │  ← 😁 User downloads
└──────────────┘
```

## ⏱️ PDF Pipeline Timing

Example timing on [input_pdfs/e2e_test.pdf](input_pdfs/e2e_test.pdf) — a 2-page, multi-language test PDF with tables and images (127 KB):

```text
Stage           Time    Share
─────────────────────────────────────────────────────
1. Encode       0.0s    ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
2. OCR          5.0s    █████████░░░░░░░░░░░░░░░░░░░░░  29%
3. Process      0.0s    ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
4. Translate   12.0s    █████████████████████░░░░░░░░░  70%
5. Render       0.2s    ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   1%
─────────────────────────────────────────────────────
TOTAL          17.2s
```

Observations:

- Translation dominates — ~70% of time is spent on Mistral Large API
- OCR is second — ~30% for Mistral OCR API
- Local processing is negligible — takes <1%

To run [scripts/pipeline_timing.py](scripts/pipeline_timing.py):

```bash
uv run python scripts/pipeline_timing.py input_pdfs/e2e_test.pdf
```

## 📦 Installation

1. Pre-requisite: install the uv Python package manager [from here](https://docs.astral.sh/uv/getting-started/installation/)

2. Clone the repository:

   ```bash
   git clone https://github.com/michellepace/pdf-to-english-py.git
   cd pdf-to-english-py
   ```

3. Run these terminal commands for first-time setup:

    ```bash
    # Install project dependencies (creates .venv/ directory)
    uv sync

    # Install pre-commit hooks (runs quality checks before each commit)
    uv run pre-commit install
    ```

4. Open in your IDE and verify setup:
   - Run `which python` → should show ../.venv/bin/python
   - Run `uv run pre-commit run --all-files` → should pass

5. Install the recommended extensions from [.vscode/extensions.json](.vscode/extensions.json).

6. Create a `.env` file in the project root with your [Mistral API key](https://admin.mistral.ai/organization/api-keys) (free):

   ```bash
   MISTRAL_API_KEY=your_api_key_here
   ```

## 🚀 Running the Application

```bash
uv run pdf-to-english
```

This launches a Gradio web interface at `http://127.0.0.1:7860` where you can upload PDFs and download English translations.

## 🛠️ Tech Stack

| Technology | Purpose |
| ------------ | --------- |
| [Mistral OCR 3](https://docs.mistral.ai/capabilities/document_ai/basic_ocr) 🤖 | Extracts text, tables, and images from PDFs as markdown with embedded HTML. |
| [Mistral Large LLM](https://docs.mistral.ai/getting-started/models/models_overview/) 🤖 | Translates markdown content while preserving formatting and structure. |
| [markdown-it-py](https://github.com/executablebooks/markdown-it-py) 🔧 | Converts markdown to HTML with passthrough for embedded HTML tables. |
| [WeasyPrint](https://weasyprint.org/) 🔧 | Renders HTML/CSS to PDF for the final translated document. |
| [Gradio](https://www.gradio.app/) | Provides the web interface for uploading and downloading PDFs. |
| [Python 3.14+](https://www.python.org/) | Runtime with modern type hints and performance improvements. |

**Dev tools:** pytest, ruff, pyright. Deployed on [Railway](https://railway.app/).

## 📁 Project Structure

| Path | Description |
| ------ | ------------- |
| [.claude/](.claude/) | Claude Code configuration and project instructions |
| [.vscode/](.vscode/) | IDE settings and recommended extensions |
| [input_pdfs/](input_pdfs/) | Input PDFs for testing (prefixed by language) |
| [output_pdfs/](output_pdfs/) | Processed PDF output from pipeline |
| [scripts/](scripts/) | CLI utilities for translation and profiling |
| [src/pdf_to_english_py/](src/pdf_to_english_py/) | Core pipeline modules: ocr, translate, render, app |
| [tests/](tests/) | Test files mirroring src/ structure |
| [x_docs/](x_docs/) | Research documentation and specification |
