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


def test_confirm_false_does_not_call_render_summary(make_form):
    """When confirm=False, render_summary should never be called."""
    frm = make_form({
        "properties": {"a": {"type": "string", "title": "A", "default": "x"}}
    })
    renderer = StdlibRenderer(frm)
    renderer.render_summary = MagicMock(return_value=True)
    with patch("builtins.input", side_effect=[""]), patch("builtins.print"):
        renderer.render(confirm=False)
    renderer.render_summary.assert_not_called()


# ---------------------------------------------------------------------------
# confirm=True — happy path
# ---------------------------------------------------------------------------


def test_confirm_true_calls_render_summary_with_user_answers(make_form):
    """When confirm=True, render_summary is called with the user-provided answers."""
    frm = make_form({
        "properties": {"name": {"type": "string", "title": "Name", "default": "Alice"}}
    })
    renderer = StdlibRenderer(frm)
    renderer.render_summary = MagicMock(return_value=True)
    with patch("builtins.input", side_effect=[""]), patch("builtins.print"):
        renderer.render(confirm=True)
    renderer.render_summary.assert_called_once_with({"name": "Alice"})


def test_confirm_true_returns_answers_when_summary_accepts(make_form):
    """Returning True from render_summary should make render() return answers."""
    frm = make_form({
        "properties": {"name": {"type": "string", "title": "Name", "default": ""}}
    })
    result = render_with_confirm(frm, ["Alice"], ["y"])
    assert result == {"name": "Alice"}


def test_confirm_true_loops_when_summary_declines_then_accepts(make_form):
    """Returning False then True from render_summary loops through questions again."""
    frm = make_form({
        "properties": {"name": {"type": "string", "title": "Name", "default": ""}}
    })
    # Inputs are interleaved: question1, summary1, question2, summary2
    # First pass: answer "wrong", decline summary ("n")
    # Second pass: answer "correct", accept summary ("y")
    all_inputs = ["wrong", "n", "correct", "y"]
    with patch("builtins.input", side_effect=all_inputs), patch("builtins.print"):
        result = StdlibRenderer(frm).render(confirm=True)
    assert result == {"name": "correct"}


def test_confirm_true_previous_answers_are_defaults_on_restart(make_form):
    """When the user restarts, previous answers appear as defaults."""
    frm = make_form({
        "properties": {"name": {"type": "string", "title": "Name", "default": ""}}
    })
    # Inputs are interleaved: question1, summary1, question2, summary2
    # First pass: "Alice"; decline ("n").
    # Second pass: press Enter (accepts "Alice" as default); confirm ("y").
    all_inputs = ["Alice", "n", "", "y"]
    with patch("builtins.input", side_effect=all_inputs), patch("builtins.print"):
        result = StdlibRenderer(frm).render(confirm=True)
    assert result == {"name": "Alice"}


def test_confirm_true_all_questions_retain_answers_on_restart(make_form):
    """When the user restarts, ALL questions retain previous answers, not just Q1."""
    frm = make_form({
        "properties": {
            "name": {"type": "string", "title": "Name", "default": ""},
            "email": {"type": "string", "title": "Email", "default": ""},
        }
    })
    # First pass: "Alice", "alice@example.com"; decline ("n").
    # Second pass: press Enter for both (accept previous answers); confirm ("y").
    all_inputs = ["Alice", "alice@example.com", "n", "", "", "y"]
    with patch("builtins.input", side_effect=all_inputs), patch("builtins.print"):
        result = StdlibRenderer(frm).render(confirm=True)
    assert result == {"name": "Alice", "email": "alice@example.com"}


def test_confirm_true_mixed_types_retain_answers_on_restart(make_form):
    """All question types retain their answers on restart: string, boolean, choice."""
    frm = make_form({
        "properties": {
            "name": {
                "type": "string",
                "title": "Name",
                "default": "default",
            },
            "flag": {
                "type": "boolean",
                "title": "Enable?",
                "default": False,
            },
            "license": {
                "type": "string",
                "title": "License",
                "default": "mit",
                "oneOf": [
                    {"const": "mit", "title": "MIT"},
                    {"const": "gpl", "title": "GPL"},
                ],
            },
        }
    })
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


def test_render_summary_prints_question_titles_and_values(make_form):
    """The default render_summary prints each question's title and value."""
    frm = make_form({
        "properties": {
            "project": {
                "type": "string",
                "title": "Project name",
                "default": "",
            }
        }
    })
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


def test_render_summary_returns_true_on_yes(make_form):
    """render_summary returns True when the user types 'y'."""
    frm = make_form({
        "properties": {"a": {"type": "string", "title": "A", "default": ""}}
    })
    renderer = StdlibRenderer(frm)
    renderer._form.start()
    renderer._form.record("a", "val", user_provided=True)
    with patch("builtins.input", return_value="y"), patch("builtins.print"):
        result = renderer.render_summary(renderer._form.user_answers)
    assert result is True


def test_render_summary_returns_true_on_empty_input(make_form):
    """render_summary returns True (default yes) when the user presses Enter."""
    frm = make_form({
        "properties": {"a": {"type": "string", "title": "A", "default": ""}}
    })
    renderer = StdlibRenderer(frm)
    renderer._form.start()
    renderer._form.record("a", "val", user_provided=True)
    with patch("builtins.input", return_value=""), patch("builtins.print"):
        result = renderer.render_summary(renderer._form.user_answers)
    assert result is True


def test_render_summary_returns_false_on_no(make_form):
    """render_summary returns False when the user types 'n'."""
    frm = make_form({
        "properties": {"a": {"type": "string", "title": "A", "default": ""}}
    })
    renderer = StdlibRenderer(frm)
    renderer._form.start()
    renderer._form.record("a", "val", user_provided=True)
    with patch("builtins.input", return_value="n"), patch("builtins.print"):
        result = renderer.render_summary(renderer._form.user_answers)
    assert result is False


def test_render_summary_reprompts_on_invalid_input(make_form):
    """render_summary re-prompts when the user enters neither y nor n."""
    frm = make_form({
        "properties": {"a": {"type": "string", "title": "A", "default": ""}}
    })
    renderer = StdlibRenderer(frm)
    renderer._form.start()
    renderer._form.record("a", "val", user_provided=True)
    with patch("builtins.input", side_effect=["maybe", "y"]), patch("builtins.print"):
        result = renderer.render_summary(renderer._form.user_answers)
    assert result is True


# ---------------------------------------------------------------------------
# render_summary() display value formatting
# ---------------------------------------------------------------------------


def test_render_summary_boolean_shows_yes_no(make_form):
    """Boolean values are shown as 'Yes' or 'No' in the summary."""
    frm = make_form({
        "properties": {"flag": {"type": "boolean", "title": "Enable?", "default": True}}
    })
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


def test_render_summary_choice_shows_option_title(make_form):
    """Choice values are resolved to their option title in the summary."""
    frm = make_form({
        "properties": {
            "license": {
                "type": "string",
                "title": "License",
                "default": "mit",
                "oneOf": [
                    {"const": "mit", "title": "MIT License"},
                    {"const": "apache", "title": "Apache 2.0"},
                ],
            }
        }
    })
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


def test_render_summary_multiple_shows_comma_separated_titles(make_form):
    """Multiple-choice values are shown as comma-separated option titles."""
    frm = make_form({
        "properties": {
            "tags": {
                "type": "array",
                "title": "Tags",
                "default": [],
                "items": {
                    "oneOf": [
                        {"const": "a", "title": "Alpha"},
                        {"const": "b", "title": "Beta"},
                    ]
                },
            }
        }
    })
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


def test_noinput_render_summary_always_returns_true(make_form):
    """NoInputRenderer.render_summary always returns True without I/O."""
    frm = make_form({
        "properties": {"a": {"type": "string", "title": "A", "default": "x"}}
    })
    renderer = NoInputRenderer(frm)
    assert renderer.render_summary({}) is True


def test_noinput_confirm_true_does_not_loop(make_form):
    """NoInputRenderer with confirm=True should complete in one pass."""
    frm = make_form({
        "properties": {"name": {"type": "string", "title": "Name", "default": "Alice"}}
    })
    renderer = NoInputRenderer(frm)
    result = renderer.render(confirm=True)
    assert result == {"name": "Alice"}
