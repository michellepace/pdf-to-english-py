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
for path in ['input_pdfs/french.pdf', 'output_pdfs/french_EN.pdf']:
    r = PdfReader(path)
    print(f'{path}: {len(r.pages)} pages')
    for i, p in enumerate(r.pages):
        w, h = float(p.mediabox.width), float(p.mediabox.height)
        print(f'  Page {i+1}: {w*25.4/72:.0f}×{h*25.4/72:.0f} mm')
"
```

## Check Embedded Images (Pixel Dimensions)

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

## Check Rendered Image Sizes (Physical mm)

Parses content stream transformation matrices to get actual rendered sizes.

### Standard PDFs (e.g. source documents)

```bash
uv run python -c "
from pypdf import PdfReader
import re

for path in ['input_pdfs/scale.pdf']:
    print(f'=== {path} ===')
    r = PdfReader(path)
    p = r.pages[0]
    data = p['/Contents'].get_object().get_data().decode('latin-1')

    # Standard PDF: a b c d e f cm ... /name Do (with possible intervening content)
    matches = re.findall(r'([\d.]+)\s+[\d.]+\s+[\d.]+\s+([\d.]+)\s+[\d.]+\s+[\d.]+\s+cm[^D]*(/\S+)\s+Do', data, re.DOTALL)
    for w_pt, h_pt, name in matches:
        w_mm = abs(float(w_pt)) * 25.4 / 72
        h_mm = abs(float(h_pt)) * 25.4 / 72
        print(f'  {name}: {w_mm:.1f} × {h_mm:.1f} mm')
"
```

### WeasyPrint PDFs (e.g. output documents)

WeasyPrint uses a 0.75 global scale factor and places transforms immediately before image draws.

```bash
uv run python -c "
from pypdf import PdfReader
import re

WEASYPRINT_SCALE = 0.75  # Global scale factor in WeasyPrint content streams

for path in ['output_pdfs/scale_EN.pdf']:
    print(f'=== {path} ===')
    r = PdfReader(path)
    for i, p in enumerate(r.pages):
        data = p['/Contents'].get_object().get_data().decode('latin-1')

        # WeasyPrint: transform matrix immediately before /name Do
        # Pattern: width 0 0 height tx ty cm\n/imageName Do
        matches = re.findall(r'([\d.]+)\s+0\s+0\s+-?([\d.]+)\s+[\d.]+\s+[\d.]+\s+cm\s*\n\s*(/\S+)\s+Do', data)
        if matches:
            print(f'  Page {i+1}:')
            for w_pt, h_pt, name in matches:
                w_mm = float(w_pt) * WEASYPRINT_SCALE * 25.4 / 72
                h_mm = float(h_pt) * WEASYPRINT_SCALE * 25.4 / 72
                print(f'    {name}: {w_mm:.1f} × {h_mm:.1f} mm')
"
```
