---
name: pdf-investigate
description: Quick comparison and analysis of PDFs using pypdf. Use when validating visual alignment of output PDFs against source PDFs, checking page dimensions, inspecting embedded images, or debugging sizing calculations.
allowed-tools: Bash(uv:*), Bash(python:*)
---

# PDF Investigation Tool

Quick comparison and analysis of PDFs using pypdf (dev dependency).

Use when validating visual alignment of output PDFs against source PDFs.

## Compare Page Dimensions

```bash
uv run python -c "
from pypdf import PdfReader
for path in ['sample_pdfs/french.pdf', 'output_pdfs/french_EN.pdf']:
    r = PdfReader(path)
    print(f'{path}: {len(r.pages)} pages')
    for i, p in enumerate(r.pages):
        w, h = float(p.mediabox.width), float(p.mediabox.height)
        print(f'  Page {i+1}: {w*25.4/72:.0f}×{h*25.4/72:.0f} mm')
"
```

## Check Embedded Images

```bash
uv run python -c "
from pypdf import PdfReader
r = PdfReader('output_pdfs/french_EN.pdf')
for i, p in enumerate(r.pages):
    if '/XObject' in p['/Resources']:
        for name, obj in p['/Resources']['/XObject'].get_object().items():
            if obj['/Subtype'] == '/Image':
                print(f'Page {i+1} {name}: {obj[\"/Width\"]}×{obj[\"/Height\"]} px')
"
```
