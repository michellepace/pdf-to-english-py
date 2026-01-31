"""Gradio web application for PDF translation."""

import os
import tempfile
from pathlib import Path

import gradio as gr
from dotenv import load_dotenv

from pdf_to_english_py.ocr import extract_pdf
from pdf_to_english_py.render import render_pdf
from pdf_to_english_py.theme import (
    ALL_CSS,
    DARK_THEME,
    FORCE_DARK_HEAD,
    pipeline_html,
)
from pdf_to_english_py.translate import translate_markdown
from pdf_to_english_py.validate import (
    validate_api_key_format,
    validate_api_key_with_mistral,
)

# Load environment variables from .env file
load_dotenv()


def api_key_default(railway_env: str | None, api_key: str | None) -> str:
    """Return API key default for the UI: empty when deployed, key value locally."""
    if railway_env:
        return ""
    return api_key or ""


def _hide_error() -> gr.Markdown:
    """Return a hidden Markdown component to clear an error message."""
    return gr.Markdown(visible=False)


def _step_error(step: str, done: set[str], msg: str) -> tuple[object, ...]:
    """Return a yield tuple that marks the current pipeline step as errored."""
    return (
        gr.skip(),
        gr.HTML(
            value=pipeline_html(active=step, done=done, error=msg),
            visible=True,
        ),
        gr.skip(),
        gr.skip(),
    )


def _step_active(
    step: str, done: set[str], *, clear_file: bool = False
) -> tuple[object, ...]:
    """Return a yield tuple that marks the current pipeline step as active."""
    return (
        gr.File(value=None) if clear_file else gr.skip(),
        gr.HTML(
            value=pipeline_html(active=step, done=done),
            visible=True,
        ),
        _hide_error() if clear_file else gr.skip(),
        _hide_error() if clear_file else gr.skip(),
    )


def _handle_translate(  # noqa: ANN202
    pdf_file: str | None,
    api_key: str,
):  # Return type omitted — Gradio evaluates annotations at runtime
    """Generator handler that drives the OCR → translate → render pipeline.

    Yields pipeline status updates as it processes the uploaded PDF
    with the user-provided API key.
    """
    api_key = api_key.strip()
    _no_error = gr.Markdown(visible=False)
    pdf_valid = pdf_file is not None
    key_valid = validate_api_key_format(api_key)

    if not pdf_valid or not key_valid:
        yield (
            gr.skip(),
            gr.skip(),
            gr.Markdown("Please upload a PDF file.", visible=not pdf_valid),
            gr.Markdown(
                "Please provide your Mistral API key.",
                visible=not key_valid,
            ),
        )
        return

    # Network validation (format already checked above)
    is_valid, error_msg, client = validate_api_key_with_mistral(api_key)
    if not is_valid or client is None:
        yield (
            gr.skip(),
            gr.skip(),
            _no_error,
            gr.Markdown(error_msg, visible=True),
        )
        return

    input_path = Path(pdf_file)
    output_dir = Path(tempfile.gettempdir())

    # Step 1: OCR
    yield _step_active("ocr", set(), clear_file=True)
    try:
        ocr_result = extract_pdf(input_path, client)
    except Exception as e:  # noqa: BLE001
        yield _step_error("ocr", set(), f"OCR failed: {e}")
        return

    # Step 2: Translation
    yield _step_active("translate", {"ocr"})
    try:
        translated_markdown = translate_markdown(ocr_result.raw_markdown, client)
    except Exception as e:  # noqa: BLE001
        yield _step_error("translate", {"ocr"}, f"Translation failed: {e}")
        return

    # Step 3: Render PDF
    yield _step_active("render", {"ocr", "translate"})
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
        yield _step_error(
            "render",
            {"ocr", "translate"},
            f"PDF rendering failed: {e}",
        )
        return

    # Complete
    yield (
        str(output_path),
        gr.HTML(value=pipeline_html(complete=True), visible=True),
        _no_error,
        _no_error,
    )


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
                    value=api_key_default(
                        os.environ.get("RAILWAY_ENVIRONMENT_NAME"),
                        os.environ.get("MISTRAL_API_KEY"),
                    ),
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
                pipeline_status = gr.HTML(visible=False)

        input_file.upload(fn=_hide_error, outputs=[pdf_error])
        input_file.clear(fn=_hide_error, outputs=[pdf_error])
        api_key_input.change(fn=_hide_error, outputs=[key_error])

        translate_btn.click(
            fn=_handle_translate,
            inputs=[input_file, api_key_input],
            outputs=[output_file, pipeline_status, pdf_error, key_error],
        )

    return demo


def main() -> None:
    """Entry point for the application."""
    app = create_app()
    app.launch(
        server_name="0.0.0.0",  # noqa: S104 - Required for Railway deployment
        server_port=int(os.environ.get("PORT", "7860")),
        theme=DARK_THEME,
        head=FORCE_DARK_HEAD,
        css=ALL_CSS,
    )


if __name__ == "__main__":
    main()
