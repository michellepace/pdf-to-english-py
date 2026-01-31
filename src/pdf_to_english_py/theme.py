"""UI theme, CSS, and pipeline display constants for the Gradio app."""

from gradio.themes import Base, Color

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
DARK_THEME = Base(
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

FORCE_DARK_HEAD = "<script>document.documentElement.classList.add('dark')</script>"

_CONTAINER_CSS = (
    ".gradio-container { max-width: 1100px !important; width: 100%; margin: auto; }"
)

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

_PIPELINE_CSS = (
    ".pipeline { display: flex; flex-direction: column; gap: 0.3rem; }"
    ".stage { display: flex; align-items: center; gap: 0.5rem;"
    " font-size: 0.833rem; color: #5a5a5e; height: 1.5rem;"
    " transition: color 0.3s ease; }"
    ".stage.active { color: #E0B48E; }"
    ".stage.done { color: #9E9E9E; }"
    ".stage-dot { width: 7px; height: 7px; border-radius: 50%;"
    " background: #27272a; flex-shrink: 0; transition: all 0.3s ease; }"
    ".stage.active .stage-dot { background: #C48B64;"
    " box-shadow: 0 0 6px rgba(196,139,100,0.5);"
    " animation: pipeline-pulse 1.6s ease-in-out infinite; }"
    ".stage.done .stage-dot { display: none; }"
    ".stage-check { display: none; color: #AD7350; flex-shrink: 0; }"
    ".stage.done .stage-check { display: flex; align-items: center; }"
    ".complete-line { display: flex; align-items: center; gap: 0.45rem;"
    " margin-top: 0.5rem; font-size: 0.833rem; color: #E0B48E;"
    " font-weight: 600; }"
    ".complete-line .check-icon { width: 18px; height: 18px;"
    " border-radius: 50%; background: #3A2418; display: grid;"
    " place-items: center; color: #D4A27F; flex-shrink: 0; }"
    ".error-line { margin-top: 0.5rem; font-size: 0.833rem;"
    " color: #ffb2ff; }"
    "@keyframes pipeline-pulse {"
    " 0%, 100% { box-shadow: 0 0 4px rgba(196,139,100,0.3); }"
    " 50% { box-shadow: 0 0 10px rgba(196,139,100,0.6); } }"
)

_TICK_SVG = (
    '<svg width="14" height="14" viewBox="0 0 24 24" fill="none"'
    ' stroke="currentColor" stroke-width="2.5" stroke-linecap="round"'
    ' stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>'
)

_PIPELINE_STEPS = (
    ("ocr", "Extracting text (OCR)\u2026"),
    ("translate", "Translating to English\u2026"),
    ("render", "Rendering PDF\u2026"),
)

# Combined CSS for the Gradio app
ALL_CSS = (
    f"{_CONTAINER_CSS} {_INPUT_ERROR_CSS} {_HIDE_FOOTER_CSS}"
    f" {_KEY_HELP_CSS} {_CONVERT_BTN_CSS} {_PIPELINE_CSS}"
)


def pipeline_html(
    *,
    active: str | None = None,
    done: set[str] | None = None,
    complete: bool = False,
    error: str | None = None,
) -> str:
    """Build HTML for the pipeline status display.

    Args:
        active: ID of the currently-running step.
        done: Set of step IDs that have completed.
        complete: If True, mark all steps done and show success message.
        error: If set, display an error message below the pipeline.

    Returns:
        HTML string for the pipeline status.
    """
    done = done or set()
    if complete:
        done = {step_id for step_id, _ in _PIPELINE_STEPS}

    lines: list[str] = []
    for step_id, label in _PIPELINE_STEPS:
        if step_id in done:
            cls = "stage done"
        elif step_id == active:
            cls = "stage active"
        else:
            cls = "stage"
        lines.append(
            f'<div class="{cls}">'
            f'<div class="stage-dot"></div>'
            f'<div class="stage-check">{_TICK_SVG}</div>'
            f"<span>{label}</span>"
            f"</div>"
        )

    html = '<div class="pipeline">' + "".join(lines) + "</div>"

    if complete:
        html += (
            '<div class="complete-line">'
            f'<div class="check-icon">{_TICK_SVG}</div>'
            "<span>Translation complete!</span>"
            "</div>"
        )

    if error:
        html += f'<div class="error-line">{error}</div>'

    return html
