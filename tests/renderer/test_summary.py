"""Tests for the summary/confirmation screen (confirm=True on render()).

The default render_summary() implementation lives on BaseRenderer and uses
plain print/input, so these tests exercise it through StdlibRenderer.
"""

from tui_forms import form
from tui_forms.renderer.noinput import NoInputRenderer
from tui_forms.renderer.stdlib import StdlibRenderer
from typing import Any
from unittest.mock import MagicMock
from unittest.mock import patch


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_form(*questions: form.BaseQuestion) -> form.Form:
    """Build a minimal Form from positional questions."""
    return form.Form(title="Test", description="", questions=list(questions))


def render_with_confirm(
    frm: form.Form, question_inputs: list[str], summary_inputs: list[str]
) -> dict[str, Any]:
    """Render *frm* with confirm=True, using separate input lists for
    the question phase and the summary confirmation phase."""
    all_inputs = question_inputs + summary_inputs
    with patch("builtins.input", side_effect=all_inputs), patch("builtins.print"):
        return StdlibRenderer(frm).render(confirm=True)


# ---------------------------------------------------------------------------
# confirm=False (default) skips the summary
# ---------------------------------------------------------------------------


def test_confirm_false_does_not_call_render_summary():
    """When confirm=False, render_summary should never be called."""
    frm = make_form(
        form.Question(key="a", type="string", title="A", description="", default="x"),
    )
    renderer = StdlibRenderer(frm)
    renderer.render_summary = MagicMock(return_value=True)
    with patch("builtins.input", side_effect=[""]), patch("builtins.print"):
        renderer.render(confirm=False)
    renderer.render_summary.assert_not_called()


# ---------------------------------------------------------------------------
# confirm=True — happy path
# ---------------------------------------------------------------------------


def test_confirm_true_calls_render_summary_with_user_answers():
    """When confirm=True, render_summary is called with the user-provided answers."""
    frm = make_form(
        form.Question(
            key="name", type="string", title="Name", description="", default="Alice"
        ),
    )
    renderer = StdlibRenderer(frm)
    renderer.render_summary = MagicMock(return_value=True)
    with patch("builtins.input", side_effect=[""]), patch("builtins.print"):
        renderer.render(confirm=True)
    renderer.render_summary.assert_called_once_with({"name": "Alice"})


def test_confirm_true_returns_answers_when_summary_accepts():
    """Returning True from render_summary should make render() return answers."""
    frm = make_form(
        form.Question(
            key="name", type="string", title="Name", description="", default=""
        ),
    )
    result = render_with_confirm(frm, ["Alice"], ["y"])
    assert result == {"name": "Alice"}


def test_confirm_true_loops_when_summary_declines_then_accepts():
    """Returning False then True from render_summary loops through questions again."""
    frm = make_form(
        form.Question(
            key="name", type="string", title="Name", description="", default=""
        ),
    )
    # Inputs are interleaved: question1, summary1, question2, summary2
    # First pass: answer "wrong", decline summary ("n")
    # Second pass: answer "correct", accept summary ("y")
    all_inputs = ["wrong", "n", "correct", "y"]
    with patch("builtins.input", side_effect=all_inputs), patch("builtins.print"):
        result = StdlibRenderer(frm).render(confirm=True)
    assert result == {"name": "correct"}


def test_confirm_true_previous_answers_are_defaults_on_restart():
    """When the user restarts, previous answers appear as defaults."""
    frm = make_form(
        form.Question(
            key="name", type="string", title="Name", description="", default=""
        ),
    )
    # Inputs are interleaved: question1, summary1, question2, summary2
    # First pass: "Alice"; decline ("n").
    # Second pass: press Enter (accepts "Alice" as default); confirm ("y").
    all_inputs = ["Alice", "n", "", "y"]
    with patch("builtins.input", side_effect=all_inputs), patch("builtins.print"):
        result = StdlibRenderer(frm).render(confirm=True)
    assert result == {"name": "Alice"}


def test_confirm_true_all_questions_retain_answers_on_restart():
    """When the user restarts, ALL questions retain previous answers, not just Q1."""
    frm = make_form(
        form.Question(
            key="name", type="string", title="Name", description="", default=""
        ),
        form.Question(
            key="email", type="string", title="Email", description="", default=""
        ),
    )
    # First pass: "Alice", "alice@example.com"; decline ("n").
    # Second pass: press Enter for both (accept previous answers); confirm ("y").
    all_inputs = ["Alice", "alice@example.com", "n", "", "", "y"]
    with patch("builtins.input", side_effect=all_inputs), patch("builtins.print"):
        result = StdlibRenderer(frm).render(confirm=True)
    assert result == {"name": "Alice", "email": "alice@example.com"}


def test_confirm_true_mixed_types_retain_answers_on_restart():
    """All question types retain their answers on restart: string, boolean, choice."""
    frm = make_form(
        form.Question(
            key="name", type="string", title="Name", description="", default="default"
        ),
        form.QuestionBoolean(
            key="flag", type="boolean", title="Enable?", description="", default=False
        ),
        form.QuestionChoice(
            key="license",
            type="string",
            title="License",
            description="",
            default="mit",
            options=[
                {"const": "mit", "title": "MIT"},
                {"const": "gpl", "title": "GPL"},
            ],
        ),
    )
    # First pass: "Alice", yes, option 2 (gpl); decline ("n").
    # Second pass: Enter, Enter, Enter (accept all previous answers); confirm ("y").
    all_inputs = ["Alice", "y", "2", "n", "", "", "", "y"]
    with patch("builtins.input", side_effect=all_inputs), patch("builtins.print"):
        result = StdlibRenderer(frm).render(confirm=True)
    assert result["name"] == "Alice"
    assert result["flag"] is True
    assert result["license"] == "gpl"


# ---------------------------------------------------------------------------
# render_summary() default implementation — output
# ---------------------------------------------------------------------------


def test_render_summary_prints_question_titles_and_values():
    """The default render_summary prints each question's title and value."""
    frm = make_form(
        form.Question(
            key="project",
            type="string",
            title="Project name",
            description="",
            default="",
        ),
    )
    renderer = StdlibRenderer(frm)
    renderer._form.start()
    renderer._form.record("project", "my-app", user_provided=True)
    with (
        patch("builtins.input", return_value="y"),
        patch("builtins.print") as mock_print,
    ):
        renderer.render_summary(renderer._form.user_answers)
    printed = " ".join(
        str(c) for call_ in mock_print.call_args_list for c in call_.args
    )
    assert "Project name" in printed
    assert "my-app" in printed


def test_render_summary_returns_true_on_yes():
    """render_summary returns True when the user types 'y'."""
    frm = make_form(
        form.Question(key="a", type="string", title="A", description="", default=""),
    )
    renderer = StdlibRenderer(frm)
    renderer._form.start()
    renderer._form.record("a", "val", user_provided=True)
    with patch("builtins.input", return_value="y"), patch("builtins.print"):
        result = renderer.render_summary(renderer._form.user_answers)
    assert result is True


def test_render_summary_returns_true_on_empty_input():
    """render_summary returns True (default yes) when the user presses Enter."""
    frm = make_form(
        form.Question(key="a", type="string", title="A", description="", default=""),
    )
    renderer = StdlibRenderer(frm)
    renderer._form.start()
    renderer._form.record("a", "val", user_provided=True)
    with patch("builtins.input", return_value=""), patch("builtins.print"):
        result = renderer.render_summary(renderer._form.user_answers)
    assert result is True


def test_render_summary_returns_false_on_no():
    """render_summary returns False when the user types 'n'."""
    frm = make_form(
        form.Question(key="a", type="string", title="A", description="", default=""),
    )
    renderer = StdlibRenderer(frm)
    renderer._form.start()
    renderer._form.record("a", "val", user_provided=True)
    with patch("builtins.input", return_value="n"), patch("builtins.print"):
        result = renderer.render_summary(renderer._form.user_answers)
    assert result is False


def test_render_summary_reprompts_on_invalid_input():
    """render_summary re-prompts when the user enters neither y nor n."""
    frm = make_form(
        form.Question(key="a", type="string", title="A", description="", default=""),
    )
    renderer = StdlibRenderer(frm)
    renderer._form.start()
    renderer._form.record("a", "val", user_provided=True)
    with patch("builtins.input", side_effect=["maybe", "y"]), patch("builtins.print"):
        result = renderer.render_summary(renderer._form.user_answers)
    assert result is True


# ---------------------------------------------------------------------------
# render_summary() display value formatting
# ---------------------------------------------------------------------------


def test_render_summary_boolean_shows_yes_no():
    """Boolean values are shown as 'Yes' or 'No' in the summary."""
    frm = make_form(
        form.QuestionBoolean(
            key="flag", type="boolean", title="Enable?", description="", default=True
        ),
    )
    renderer = StdlibRenderer(frm)
    renderer._form.start()
    renderer._form.record("flag", True, user_provided=True)
    with (
        patch("builtins.input", return_value="y"),
        patch("builtins.print") as mock_print,
    ):
        renderer.render_summary(renderer._form.user_answers)
    printed = " ".join(
        str(c) for call_ in mock_print.call_args_list for c in call_.args
    )
    assert "Yes" in printed


def test_render_summary_choice_shows_option_title():
    """Choice values are resolved to their option title in the summary."""
    frm = make_form(
        form.QuestionChoice(
            key="license",
            type="string",
            title="License",
            description="",
            default="mit",
            options=[
                {"const": "mit", "title": "MIT License"},
                {"const": "apache", "title": "Apache 2.0"},
            ],
        ),
    )
    renderer = StdlibRenderer(frm)
    renderer._form.start()
    renderer._form.record("license", "mit", user_provided=True)
    with (
        patch("builtins.input", return_value="y"),
        patch("builtins.print") as mock_print,
    ):
        renderer.render_summary(renderer._form.user_answers)
    printed = " ".join(
        str(c) for call_ in mock_print.call_args_list for c in call_.args
    )
    assert "MIT License" in printed


def test_render_summary_multiple_shows_comma_separated_titles():
    """Multiple-choice values are shown as comma-separated option titles."""
    frm = make_form(
        form.QuestionMultiple(
            key="tags",
            type="array",
            title="Tags",
            description="",
            default=[],
            options=[
                {"const": "a", "title": "Alpha"},
                {"const": "b", "title": "Beta"},
            ],
        ),
    )
    renderer = StdlibRenderer(frm)
    renderer._form.start()
    renderer._form.record("tags", ["a", "b"], user_provided=True)
    with (
        patch("builtins.input", return_value="y"),
        patch("builtins.print") as mock_print,
    ):
        renderer.render_summary(renderer._form.user_answers)
    printed = " ".join(
        str(c) for call_ in mock_print.call_args_list for c in call_.args
    )
    assert "Alpha" in printed
    assert "Beta" in printed


# ---------------------------------------------------------------------------
# NoInputRenderer — render_summary always returns True
# ---------------------------------------------------------------------------


def test_noinput_render_summary_always_returns_true():
    """NoInputRenderer.render_summary always returns True without I/O."""
    frm = make_form(
        form.Question(key="a", type="string", title="A", description="", default="x"),
    )
    renderer = NoInputRenderer(frm)
    assert renderer.render_summary({}) is True


def test_noinput_confirm_true_does_not_loop():
    """NoInputRenderer with confirm=True should complete in one pass."""
    frm = make_form(
        form.Question(
            key="name", type="string", title="Name", description="", default="Alice"
        ),
    )
    renderer = NoInputRenderer(frm)
    result = renderer.render(confirm=True)
    assert result == {"name": "Alice"}
