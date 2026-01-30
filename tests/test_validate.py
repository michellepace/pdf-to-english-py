"""Tests for validation module."""

import os

import pytest

from pdf_to_english_py.validate import (
    validate_api_key_format,
    validate_api_key_with_mistral,
)


class TestValidateApiKeyFormat:
    """Tests for API key format validation."""

    def test_returns_false_for_empty_string(self) -> None:
        """Empty string is not a valid API key."""
        assert validate_api_key_format("") is False

    def test_returns_false_for_whitespace_only(self) -> None:
        """Whitespace-only string is not a valid API key."""
        assert validate_api_key_format("   ") is False

    def test_returns_true_for_non_empty_string(self) -> None:
        """Non-empty string passes format validation."""
        assert validate_api_key_format("some-api-key-123") is True


class TestValidateApiKeyWithMistral:
    """Tests for Mistral API key validation."""

    @pytest.mark.integration
    def test_invalid_key_returns_false_with_error_message(self) -> None:
        """Invalid API key should return False with an error message."""
        is_valid, error_msg, client = validate_api_key_with_mistral("invalid-key-12345")

        assert is_valid is False
        assert "invalid api key" in error_msg.lower()
        assert client is None

    @pytest.mark.integration
    def test_valid_key_returns_true(self) -> None:
        """Valid API key should return True with empty error message."""
        api_key = os.environ.get("MISTRAL_API_KEY")
        if not api_key:
            pytest.skip("MISTRAL_API_KEY not set")

        is_valid, error_msg, client = validate_api_key_with_mistral(api_key)

        assert is_valid is True
        assert error_msg == ""
        assert client is not None
