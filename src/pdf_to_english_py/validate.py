"""Validation functions for API key and input checks."""

from mistralai import Mistral
from mistralai.models import NoResponseError, SDKError


def validate_api_key_format(api_key: str) -> bool:
    """Check if API key has valid format (non-empty, non-whitespace).

    Args:
        api_key: The API key string to validate.

    Returns:
        True if api_key is a non-empty, non-whitespace string.
    """
    return bool(api_key.strip())


def validate_api_key_with_mistral(api_key: str) -> tuple[bool, str, Mistral | None]:
    """Validate API key by making a lightweight Mistral API call.

    Creates a client and calls models.list() to verify the key.
    On success, returns the validated client for reuse.

    Args:
        api_key: The Mistral API key to validate.

    Returns:
        Tuple of (is_valid, error_message, client).
        error_message is empty string and client is the Mistral instance if valid.
        client is None if validation failed.
    """
    try:
        client = Mistral(api_key=api_key)
        client.models.list()
    except SDKError:
        return (
            False,
            "Invalid API key. Please check your Mistral API key and try again.",
            None,
        )
    except NoResponseError:
        return (
            False,
            "Could not reach Mistral API."
            " Please check your internet connection and try again.",
            None,
        )
    except Exception:  # noqa: BLE001
        return (
            False,
            "Validation failed unexpectedly. Please try again.",
            None,
        )
    return True, "", client
