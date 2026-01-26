"""Translation module using Mistral Large."""

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mistralai import Mistral

TRANSLATION_SYSTEM_PROMPT = """\
You are a professional translator specialising in document translation.
Translate the following document to British English.

CRITICAL RULES - YOU MUST FOLLOW THESE EXACTLY:

1. PRESERVE ALL HTML TAGS EXACTLY AS THEY APPEAR:
   - Keep all <table>, <tr>, <td>, <th> tags unchanged
   - Keep all attributes like colspan="2", rowspan="3" exactly as written
   - Keep all <div>, <span>, and other HTML tags with their attributes

2. PRESERVE ALL MARKDOWN FORMATTING:
   - Keep headers (# ## ###) at the start of lines
   - Keep bold (**text**) and italic (*text*) markers
   - Keep list markers (- or *)
   - Keep code blocks and inline code

3. PRESERVE ALL IMAGE PLACEHOLDERS EXACTLY:
   - Keep ![filename](IMG_PLACEHOLDER_N) format unchanged
   - Do not modify image filenames or placeholder values

4. ONLY TRANSLATE THE ACTUAL TEXT CONTENT:
   - Translate text inside HTML tags
   - Do NOT translate HTML attribute values
   - Do NOT translate URLs, file paths, or code

5. MAINTAIN DOCUMENT STRUCTURE:
   - Keep the same line breaks and spacing
   - Keep the same paragraph structure

Return ONLY the translated document. Do not add explanations or notes."""


def strip_images(markdown: str) -> tuple[str, dict[str, str]]:
    """Strip base64 images from markdown, replacing with placeholders.

    Args:
        markdown: Markdown content potentially containing base64 data URIs.

    Returns:
        Tuple of (stripped markdown, dict mapping placeholders to data URIs).
    """
    pattern = r"!\[([^\]]*)\]\((data:image/[^)]+)\)"
    images: dict[str, str] = {}
    counter = 0

    def replacer(match: re.Match[str]) -> str:
        nonlocal counter
        alt_text, data_uri = match.group(1), match.group(2)
        placeholder = f"IMG_PLACEHOLDER_{counter}"
        images[placeholder] = data_uri
        counter += 1
        return f"![{alt_text}]({placeholder})"

    return re.sub(pattern, replacer, markdown), images


def restore_images(markdown: str, images: dict[str, str]) -> str:
    """Restore base64 images from placeholders.

    Args:
        markdown: Markdown with placeholders.
        images: Dict mapping placeholders to original data URIs.

    Returns:
        Markdown with base64 images restored.
    """
    result = markdown
    for placeholder, data_uri in images.items():
        result = result.replace(f"]({placeholder})", f"]({data_uri})")
    return result


def translate_markdown(
    markdown: str,
    client: Mistral,
) -> str:
    """Translate markdown content while preserving HTML and formatting.

    Uses Mistral Large with explicit prompting to preserve:
    - HTML tags (tables with colspan/rowspan)
    - Markdown formatting (headers, bold, lists)
    - Image placeholders (IMG_PLACEHOLDER_N)

    Base64 images are stripped before translation and restored after to reduce
    token usage — images don't need translation.

    Args:
        markdown: Source markdown with embedded HTML tables and images.
        client: Mistral API client.

    Returns:
        Markdown translated to British English with all formatting preserved.
    """
    # Strip base64 images to reduce token usage
    stripped_markdown, images = strip_images(markdown)

    response = client.chat.complete(
        model="mistral-large-latest",
        messages=[
            {"role": "system", "content": TRANSLATION_SYSTEM_PROMPT},
            {"role": "user", "content": stripped_markdown},
        ],
    )

    # Extract the translated content
    content = response.choices[0].message.content
    if isinstance(content, str):
        # Restore base64 images after translation
        return restore_images(content, images)
    return ""
