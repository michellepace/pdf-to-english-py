# CLAUDE.md

Use British spelling throughout.

## Project Purpose

Python prototype for Mistral OCR PDF translation pipeline — extract text from PDFs, translate to English, generate styled PDF output.

## Tech Stack

- **Python 3.14+** with **uv** package manager
- **Gradio** — web interface
- **Mistral AI** — OCR (`mistral-ocr-latest`) and translation (`mistral-large-latest`)
- **WeasyPrint** — PDF generation from HTML/CSS
- **Ruff** — linting (ALL rules enabled) and formatting
- **Pyright** — type checking
- **pytest** — testing

Quality config lives in `pyproject.toml`; pre-commit runs Ruff, Pyright, and pytest on every commit.

## Project Structure

UV-based Python 3.14+ with TDD workflow:

- `src/pdf_to_english_py/` — package source code
- `scripts/` — standalone utilities
- `tests/` — mirrors `src/` structure
- `input_pdfs/` — input PDFs for testing
- `x_docs/` — research documentation and prompts

## UV Workflow (Strict)

- Use `uv run` — never activate venv
- Use `uv add` — never pip
- Use `pyproject.toml` — never hand-edit `requirements.txt` (auto-generated for Railway)

```bash
# Setup & Dependencies
uv sync                                    # Match packages to lockfile
uv add --dev <pkg>                         # Add dev dependency
uv tree                                    # Show installed dependencies
uv lock --upgrade-package <pkg>            # Update specific package
uv lock --upgrade && uv sync               # Update all packages and apply

# Run the app
uv run pdf-to-english                      # Launch Gradio web interface

# Development
uv run pre-commit run --all-files          # Quality checks
uv run pytest                              # All tests
uv run pytest -v tests/test_specific.py::test_function
uv run ruff check --fix                    # Lint and auto-fix
uv run ruff format                         # Format
```

## Deployment (Railway)

Auto-deploys from `main` on push. Builds from `requirements.txt`, which the
`generate-requirements` pre-commit hook regenerates from `pyproject.toml`/`uv.lock`.

```bash
railway status              # deployment state + live URL
railway logs --build        # confirm a deploy picked up the latest commit
```

- Live: <https://pdf-to-english-prototype.up.railway.app>
- CLI is npm-based (`@railway/cli`), not a `uv` tool; `railway login` is interactive.

## Code Design Principles: Elegant Simplicity over Over-Engineered

**TDD-Driven Design**: Write tests first - this naturally creates better architecture:

- **Pure functions preferred** - no side effects in business logic, easier to test
- **Clear module boundaries** - easier to test and understand
- **Single responsibility** - complex functions are hard to test

**Key Architecture Guidelines**:

- **Layer separation** - CLI → business logic → I/O
- **One module, one purpose** - each `.py` file has one clear role
- **Handle errors at boundaries** - Catch exceptions in CLI layer, not business logic
- **Type hints required** - All function signatures need type annotations
- **Descriptive naming** - names clearly indicate purpose, consistent throughout

## TDD Implementation

- Use pytest's `tmp_path` fixture to avoid creating test files
- Avoid mocks - they add unnecessary complexity
- Test incrementally: One test should drive one behaviour
- Focused test names that describe the behaviour

## Code Quality Standards

- **Ruff**: Linting (ALL rules enabled)
- **Pyright**: Type checking (see [pyproject.toml](../pyproject.toml))
- **Pre-commit**: Auto-runs on every commit
