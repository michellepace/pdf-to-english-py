"""Tests for Gradio app module."""

from typing import TYPE_CHECKING

import gradio as gr

if TYPE_CHECKING:
    from pathlib import Path

from pdf_to_english_py.app import create_app, process_pdf


class TestCreateApp:
    """Tests for create_app function."""

    def test_returns_gradio_blocks(self) -> None:
        """Should return a Gradio Blocks instance."""
        app = create_app()

        assert isinstance(app, gr.Blocks)

    def test_app_has_title(self) -> None:
        """App should have a title configured."""
        app = create_app()

        # Blocks has a title attribute
        assert app.title is not None


class TestProcessPdf:
    """Unit tests for process_pdf function."""

    def test_returns_error_status_for_invalid_file(self, tmp_path: Path) -> None:
        """Should return error status for non-existent file."""
        # Client is not used when file doesn't exist, so we can pass None
        output_path, status = process_pdf(
            "/nonexistent/file.pdf",
            None,  # type: ignore[arg-type]
            tmp_path,
        )

        assert output_path is None
        assert "error" in status.lower()
