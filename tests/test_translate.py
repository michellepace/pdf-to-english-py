"""Tests for translation module."""

from pdf_to_english_py.translate import (
    TRANSLATION_SYSTEM_PROMPT,
    restore_images,
    strip_images,
)


class TestTranslationSystemPrompt:
    """Tests for the translation system prompt."""

    def test_prompt_mentions_html_preservation(self) -> None:
        """The prompt should instruct to preserve HTML tags."""
        assert "HTML" in TRANSLATION_SYSTEM_PROMPT
        assert "table" in TRANSLATION_SYSTEM_PROMPT.lower()

    def test_prompt_mentions_markdown_preservation(self) -> None:
        """The prompt should instruct to preserve markdown formatting."""
        assert "markdown" in TRANSLATION_SYSTEM_PROMPT.lower()

    def test_prompt_mentions_image_preservation(self) -> None:
        """The prompt should instruct to preserve image references."""
        assert "image" in TRANSLATION_SYSTEM_PROMPT.lower()


class TestStripImages:
    """Tests for stripping base64 images before translation."""

    def test_extracts_base64_images_from_markdown(self) -> None:
        """Should extract base64 images and return placeholder mapping."""
        markdown = "# Title\n\n![photo](data:image/png;base64,iVBORw0KGgo...)\n\nText"
        stripped, images = strip_images(markdown)

        assert "data:image/png;base64" not in stripped
        assert "IMG_PLACEHOLDER_0" in stripped
        assert len(images) == 1
        assert images["IMG_PLACEHOLDER_0"].startswith("data:image/png;base64")

    def test_handles_multiple_images(self) -> None:
        """Should handle multiple images with unique placeholders."""
        markdown = "![a](data:image/jpeg;base64,abc)\n![b](data:image/png;base64,xyz)"
        stripped, images = strip_images(markdown)

        assert len(images) == 2
        assert "IMG_PLACEHOLDER_0" in stripped
        assert "IMG_PLACEHOLDER_1" in stripped

    def test_preserves_non_base64_images(self) -> None:
        """Should not strip regular URL images."""
        markdown = "![photo](https://example.com/img.png)"
        stripped, images = strip_images(markdown)

        assert stripped == markdown
        assert len(images) == 0


class TestRestoreImages:
    """Tests for restoring images after translation."""

    def test_restores_images_from_placeholders(self) -> None:
        """Should restore base64 images from placeholder mapping."""
        translated = "# Title\n\n![photo](IMG_PLACEHOLDER_0)\n\nText"
        images = {"IMG_PLACEHOLDER_0": "data:image/png;base64,iVBORw0KGgo..."}
        result = restore_images(translated, images)

        assert "IMG_PLACEHOLDER_0" not in result
        assert "data:image/png;base64,iVBORw0KGgo..." in result
