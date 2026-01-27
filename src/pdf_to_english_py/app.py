"""Gradio web application for PDF translation."""

import os
import shutil
import tempfile
from pathlib import Path

import gradio as gr
from dotenv import load_dotenv
from mistralai import Mistral

from pdf_to_english_py.ocr import extract_pdf
from pdf_to_english_py.render import render_pdf
from pdf_to_english_py.translate import translate_markdown

# Load environment variables from .env file
load_dotenv()


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
    try:
        # Validate input file exists
        input_path = Path(pdf_path)
        if not input_path.exists():
            return None, f"Error: File not found: {pdf_path}"

        # Step 1: Extract text using OCR
        ocr_result = extract_pdf(input_path, client)

        # Step 2: Translate to English
        translated_markdown = translate_markdown(ocr_result.raw_markdown, client)

        # Step 3: Render to PDF
        output_filename = f"{input_path.stem}_english.pdf"
        output_path = output_dir / output_filename
        render_pdf(translated_markdown, output_path)

        return str(output_path), "Translation complete!"

    except FileNotFoundError as e:
        return None, f"Error: File not found - {e}"
    except Exception as e:  # noqa: BLE001
        return None, f"Error: {e}"


def _create_gradio_handler() -> tuple[gr.File, gr.Textbox] | tuple[None, str]:
    """Create a handler function for Gradio that manages the Mistral client.

    Returns:
        A function that processes uploaded PDFs.
    """
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        return None, "Error: MISTRAL_API_KEY not set in environment"

    client = Mistral(api_key=api_key)

    def handler(pdf_file: str | None) -> tuple[str | None, str]:
        if pdf_file is None:
            return None, "Please upload a PDF file"

        # Debug: log what Gradio passes
        print(f"DEBUG: pdf_file type={type(pdf_file)}, value={pdf_file!r}")

        # Extract file path - Gradio 3.x passes the path as a string
        if isinstance(pdf_file, str):
            file_path = pdf_file
        elif hasattr(pdf_file, "name"):
            file_path = pdf_file.name
        else:
            return None, f"Error: Unexpected file type: {type(pdf_file)}"

        print(f"DEBUG: file_path={file_path}")

        # Create temporary directory for output
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path, status = process_pdf(
                file_path,
                client,
                Path(tmp_dir),
            )

            if output_path is None:
                return None, status

            # Copy to a persistent location for download
            # Gradio needs the file to persist after the handler returns
            persistent_path = Path(tempfile.gettempdir()) / Path(output_path).name
            shutil.copy(output_path, persistent_path)
            return str(persistent_path), status

    return handler  # type: ignore[return-value]


def create_app() -> gr.Blocks:
    """Create and configure the Gradio interface.

    Returns:
        Configured Gradio Blocks application.
    """
    with gr.Blocks(title="PDF To English") as demo:
        gr.Markdown("<br>")
        gr.Markdown("# PDF To English")
        gr.Markdown(
            "Upload a PDF and download an English translation.\n\n"
            "Powered by Mistral OCR to extract text, tables, and images, "
            "Mistral Large for translation, then rendered back into a PDF."
        )

        with gr.Row():
            with gr.Column():
                input_file = gr.File(
                    label="Upload PDF",
                    file_types=[".pdf"],
                )
                translate_btn = gr.Button("Translate", variant="primary")

            with gr.Column():
                output_file = gr.File(label="Download English PDF")
                status = gr.Textbox(label="Status", interactive=False)

        # Create handler with API client
        handler = _create_gradio_handler()

        if callable(handler):
            translate_btn.click(
                fn=handler,
                inputs=[input_file],
                outputs=[output_file, status],
            )
        else:
            # Handler creation failed - show error
            status.value = handler[1] if isinstance(handler, tuple) else "Setup error"

    return demo


def main() -> None:
    """Entry point for the application."""
    app = create_app()
    app.launch(
        server_name="0.0.0.0",  # noqa: S104 - Required for Railway deployment
        server_port=int(os.environ.get("PORT", "7860")),
    )


if __name__ == "__main__":
    main()
