"""Gradio web application for PDF translation."""

import os
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

import gradio as gr
from dotenv import load_dotenv
from gradio.themes import Base, Color

if TYPE_CHECKING:
    from collections.abc import Callable

    from mistralai import Mistral

from pdf_to_english_py.ocr import extract_pdf
from pdf_to_english_py.render import render_pdf
from pdf_to_english_py.translate import translate_markdown
from pdf_to_english_py.validate import (
    validate_api_key_format,
    validate_api_key_with_mistral,
)

# Load environment variables from .env file
load_dotenv()

# Custom copper accent colour palette
_COPPER = Color(
    c50="#FDF8F4",
    c100="#F5E6D8",
    c200="#EACDB3",
    c300="#E0B48E",
    c400="#D4A27F",
    c500="#C48B64",
    c600="#AD7350",
    c700="#8F5C3D",
    c800="#6E462F",
    c900="#4D3121",
    c950="#3A2418",
    name="copper",
)

# Dark theme with warm copper accents and zinc neutrals
_DARK_THEME = Base(
    primary_hue=_COPPER,
    neutral_hue="zinc",
).set(
    body_background_fill="#09090b",
    body_text_color="#DEDEDE",
    body_text_color_subdued="#9E9E9E",
    body_background_fill_dark="#09090b",
    body_text_color_dark="#DEDEDE",
    body_text_color_subdued_dark="#9E9E9E",
)

_FORCE_DARK_HEAD = "<script>document.documentElement.classList.add('dark')</script>"

_HIDE_FOOTER_CSS = "footer { display: none !important; }"

_KEY_HELP_CSS = (
    ".key-help { margin-top: -0.2rem !important; }"
    ".key-help p { font-size: 0.833rem; color: #5a5a5e; margin: 0 !important; }"
    ".key-help a { color: #C48B64; text-decoration: none; }"
    ".key-help a:hover { color: #E0B48E; }"
)

_CONVERT_BTN_CSS = (
    ".convert-btn { width: 50% !important; margin-left: auto !important; }"
)

_INPUT_ERROR_CSS = (
    ".input-error p {"
    " color: #ffb2ff !important;"
    " margin: 0 !important;"
    " text-align: left;"
    " }"
)


def process_pdf(
    pdf_path: str,
    client: Mistral,
    output_dir: Path,
) -> tuple[str | None, str]:
    """Process a PDF and return translated English PDF.

    Orchestrates the full translation pipeline:
    1. Extract text via OCR
    2. Translate to English
    3. Render to PDF

    Args:
        pdf_path: Path to the uploaded PDF file.
        client: Mistral API client.
        output_dir: Directory for the output PDF.

    Returns:
        Tuple of (output_path, status_message).
        output_path is None if an error occurred.
    """
    input_path = Path(pdf_path)
    if not input_path.exists():
        return None, f"File not found: {pdf_path}"

    try:
        ocr_result = extract_pdf(input_path, client)
    except Exception as e:  # noqa: BLE001
        return None, f"OCR failed: {e}"

    try:
        translated_markdown = translate_markdown(ocr_result.raw_markdown, client)
    except Exception as e:  # noqa: BLE001
        return None, f"Translation failed: {e}"

    try:
        output_filename = f"{input_path.stem}_english.pdf"
        output_path = output_dir / output_filename
        render_pdf(
            translated_markdown,
            output_path,
            images=ocr_result.images,
            page_dimensions=ocr_result.page_dimensions,
        )
    except Exception as e:  # noqa: BLE001
        return None, f"PDF rendering failed: {e}"

    return str(output_path), "Translation complete!"


def _hide_error() -> gr.Markdown:
    """Return a hidden Markdown component to clear an error message."""
    return gr.Markdown(visible=False)


def _create_gradio_handler() -> Callable[..., tuple[object, ...]]:
    """Create a handler function for Gradio.

    Returns:
        A function that processes uploaded PDFs with a user-provided API key.
    """

    def handler(
        pdf_file: str | None,
        api_key: str,
    ) -> tuple[object, ...]:
        api_key = api_key.strip()
        _no_error = gr.Markdown(visible=False)
        pdf_valid = pdf_file is not None
        key_valid = validate_api_key_format(api_key)

        if not pdf_valid or not key_valid:
            return (
                gr.skip(),
                gr.skip(),
                gr.Markdown("Please upload a PDF file.", visible=not pdf_valid),
                gr.Markdown(
                    "Please provide your Mistral API key.",
                    visible=not key_valid,
                ),
            )

        # Network validation (format already checked above)
        is_valid, error_msg, client = validate_api_key_with_mistral(api_key)
        if not is_valid or client is None:
            return (
                gr.skip(),
                gr.skip(),
                _no_error,
                gr.Markdown(error_msg, visible=True),
            )

        output_path, status = process_pdf(
            pdf_file,
            client,
            Path(tempfile.gettempdir()),
        )

        return output_path, status, _no_error, _no_error

    return handler


def create_app() -> gr.Blocks:
    """Create and configure the Gradio interface.

    Returns:
        Configured Gradio Blocks application.
    """
    # Purge cached uploads and outputs older than 1 hour (checked hourly)
    with gr.Blocks(title="PDF To English", delete_cache=(3600, 3600)) as demo:
        gr.Markdown("<br>")
        gr.Markdown("# PDF To English")
        gr.Markdown("Upload a PDF, get English.")
        gr.Markdown("<br>")

        with gr.Row():
            with gr.Column():
                pdf_error = gr.Markdown(visible=False, elem_classes=["input-error"])
                input_file = gr.File(
                    label="Upload PDF",
                    file_types=[".pdf"],
                )
                key_error = gr.Markdown(visible=False, elem_classes=["input-error"])
                api_key_input = gr.Textbox(
                    label="Mistral Key",
                    placeholder="Enter your Mistral API key",
                    value=os.environ.get("MISTRAL_API_KEY", ""),
                )
                gr.Markdown(
                    "Need a key? "
                    "[Get one free \u2192]"
                    "(https://admin.mistral.ai/organization/api-keys)",
                    elem_classes=["key-help"],
                )
                translate_btn = gr.Button(
                    "Convert To English",
                    variant="primary",
                    elem_classes=["convert-btn"],
                )

            with gr.Column():
                output_file = gr.File(label="Download English PDF")
                status = gr.Textbox(label="Status", interactive=False)

        input_file.upload(fn=_hide_error, outputs=[pdf_error])
        input_file.clear(fn=_hide_error, outputs=[pdf_error])
        api_key_input.change(fn=_hide_error, outputs=[key_error])

        handler = _create_gradio_handler()
        translate_btn.click(
            fn=handler,
            inputs=[input_file, api_key_input],
            outputs=[output_file, status, pdf_error, key_error],
        )

    return demo


def main() -> None:
    """Entry point for the application."""
    app = create_app()
    app.launch(
        server_name="0.0.0.0",  # noqa: S104 - Required for Railway deployment
        server_port=int(os.environ.get("PORT", "7860")),
        theme=_DARK_THEME,
        head=_FORCE_DARK_HEAD,
        css=f"{_INPUT_ERROR_CSS} {_HIDE_FOOTER_CSS} {_KEY_HELP_CSS} {_CONVERT_BTN_CSS}",
    )


if __name__ == "__main__":
    main()
