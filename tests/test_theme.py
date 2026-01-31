"""Tests for theme module pipeline HTML generation."""

from pdf_to_english_py.theme import pipeline_html


class TestPipelineHtml:
    """Tests for pipeline_html function."""

    def test_pending_state_has_no_active_or_done_classes(self) -> None:
        """All stages should have plain 'stage' class when nothing is active."""
        html = pipeline_html()

        assert html.count('class="stage"') == 3
        assert "stage active" not in html
        assert "stage done" not in html

    def test_active_step_gets_active_class(self) -> None:
        """The active step should get 'stage active' class."""
        html = pipeline_html(active="translate")

        assert 'class="stage active"' in html
        assert html.count("stage active") == 1

    def test_done_steps_get_done_class(self) -> None:
        """Completed steps should get 'stage done' class."""
        html = pipeline_html(active="render", done={"ocr", "translate"})

        assert html.count("stage done") == 2
        assert html.count("stage active") == 1

    def test_complete_marks_all_done(self) -> None:
        """Complete state should mark all steps done and show success message."""
        html = pipeline_html(complete=True)

        assert html.count("stage done") == 3
        assert "stage active" not in html
        assert "Translation complete!" in html

    def test_error_renders_error_message(self) -> None:
        """Error message should appear in an error-line div."""
        html = pipeline_html(active="ocr", error="OCR failed: timeout")

        assert "error-line" in html
        assert "OCR failed: timeout" in html
