# Task: Research and Plan PDF-to-English Prototype

## Objective

Research and create a high-level plan for a Python prototype that:

1. Uses Mistral OCR 3 to extract text from a French PDF
2. Translates the extracted text to English (using Mistral)
3. Renders the translation as a new PDF

Write the plan to: `high-level-prototype-plan.md` (project root)

---

## Constraints

- **Python only** — use `uv` for project setup (NOT pip)
- **Official sources only** — UV, Mistral, WeasyPrint docs
- **Project location:** `~/projects/python/pdf-to-eng-prototype`

---

## Proposed Pipeline (to validate)

```text
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  French PDF │ ──> │ Mistral OCR │ ──> │  Translate  │ ──> │ English PDF │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                     markdown+HTML      Mistral Large         WeasyPrint
```

**Assumptions to validate:**

- Translation preserves HTML table structure
- WeasyPrint renders Mistral OCR output correctly

---

## Research Tasks

### 1. UV Project Setup

**Sources (in order):**

1. Run `/ask-docs uv` to confirm best practice setup commands
2. Reference `~/projects/python/uv-template/README.md` and `CLAUDE.md` for patterns and commands (do NOT copy — this template may be over-engineered for our needs)

**Determine:** Minimal commands to initialise a UV project with dev dependencies etc.

### 2. Mistral OCR 3 Output Format

**Sources:**

1. <https://raw.githubusercontent.com/mistralai/cookbook/refs/heads/main/third_party/gradio/MistralOCR.md>
2. `tool_usage.ipynb` in project root (LARGE FILE — launch subagent to investigate)
3. Use Exa MCP (`mcp__exa__get_code_context_exa`) for code examples if needed
   - Restrict to official Mistral sources

**Determine:**

- Exact output format (JSON structure with markdown? HTML tables?)
- How tables with merged cells are represented
- Feasibility of WeasyPrint for PDF generation

### 3. Mistral Translation

Assume `mistral-large`

**Determine:**

- API call pattern for translation

### 4. PDF Generation with WeasyPrint

**Sources:** Official WeasyPrint docs

**Determine:**

- How to convert Mistral OCR markdown+HTML output to PDF
- CSS requirements for table styling
- Appropriateness of WeasyPrint for PDF generation from Mistral OCR 3

---

## Required Plan Outputs

1. **UV setup commands** — exact bash commands to create project
2. **Architecture diagram** — ASCII showing: PDF → OCR → Translate → PDF Generation
3. **Code snippets** — Mistral OCR call, translation call, WeasyPrint usage
4. **Dependencies list** — packages needed (mistralai, weasyprint, etc.)

---

## Subagent Strategy

| Task | Agent Type | Notes |
|------|------------|-------|
| UV best practices | `/ask-docs uv` | Validate setup commands |
| UV template exploration | Explore | Read README.md, CLAUDE.md only |
| tool_usage.ipynb | Explore | File is large — extract Mistral patterns only |
| Mistral cookbook | WebFetch | Fetch and analyse OCR example |
| WeasyPrint docs | WebFetch/Exa | Confirm HTML table support |
