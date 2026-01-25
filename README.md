# pdf-to-english-py

Prototype Mistral OCR pipeline for [pdf-to-english](https://github.com/michellepace/pdf-to-english).

## 📁 Project Structure

| Path | Description |
|------|-------------|
| [.claude/](.claude/) | Claude Code `CLAUDE.md`, rules, settings, commands etc. |
| .venv/ | Virtual environment created by `uv sync` (gitignored) |
| [.vscode/](.vscode/) | IDE settings and recommended extensions |
| [sample_pdfs/](sample_pdfs/) | Sample PDFs for testing |
| [notebooks/](notebooks/) | Jupyter notebooks saving cleanly to Git |
| [scripts/](scripts/) | Sometimes you want a standalone script |
| [src/pdf_to_english_py/](src/pdf_to_english_py/) | Package source code |
| [tests/](tests/) | Test files mirroring src/ structure |
| x_docs/ | Research documentation and prompts |

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

## 📓 Jupyter Notebook Git Integration (Recommended)

This project uses [nbstripout](https://github.com/kynan/nbstripout) to keep notebooks clean in Git.

**One-time global setup:**

```bash
uv tool install nbstripout
nbstripout --install --global
```

Any repo with `*.ipynb filter=nbstripout` in `.gitattributes` will automatically strip outputs on commit.
