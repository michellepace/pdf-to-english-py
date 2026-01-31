"""Tests for Gradio app module."""

import gradio as gr

from pdf_to_english_py.app import api_key_default, create_app


class TestApiKeyDefault:
    """Tests for api_key_default function."""

    def test_returns_empty_when_deployed(self) -> None:
        """Should return empty string when Railway environment is set."""
        assert api_key_default("production", "sk-secret-key") == ""

    def test_returns_api_key_locally(self) -> None:
        """Should return API key when not deployed."""
        assert api_key_default(None, "sk-secret-key") == "sk-secret-key"

    def test_returns_empty_when_no_key_locally(self) -> None:
        """Should return empty string when no key is available locally."""
        assert api_key_default(None, None) == ""

    def test_returns_empty_when_deployed_without_key(self) -> None:
        """Should return empty string when deployed with no key."""
        assert api_key_default("production", None) == ""


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
