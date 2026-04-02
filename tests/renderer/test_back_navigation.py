"""Tests for back-navigation support across renderers.

These tests exercise the ``<`` back-command through the StdlibRenderer (which
is the simplest to patch) and verify that the base-class logic in
``_ask_questions`` and ``_dispatch`` handles all edge cases correctly.
"""

from tui_forms import form
from tui_forms.renderer.stdlib import StdlibRenderer
from unittest.mock import patch


# ---------------------------------------------------------------------------
# Basic back navigation
# ---------------------------------------------------------------------------


def test_back_on_second_question_rerenders_first(make_form, render_stdlib):
    """Typing ``<`` at question 2 should re-ask question 1."""
    frm = make_form({
        "properties": {
            "a": {"type": "string", "title": "A", "default": ""},
            "b": {"type": "string", "title": "B", "default": ""},
        }
    })
    # answer "first", go back, re-answer "corrected", then answer "second"
    result = render_stdlib(frm, ["first", "<", "corrected", "second"])
    assert result["a"] == "corrected"
    assert result["b"] == "second"


def test_back_on_first_question_stays_at_first(make_form, render_stdlib):
    """Typing ``<`` at the very first question should keep question 1 active."""
    frm = make_form({
        "properties": {
            "a": {"type": "string", "title": "A", "default": ""},
            "b": {"type": "string", "title": "B", "default": ""},
        }
    })
    # ``<`` at first question is a no-op; user answers normally on retry
    result = render_stdlib(frm, ["<", "hello", "world"])
    assert result["a"] == "hello"
    assert result["b"] == "world"


def test_back_multiple_times(make_form, render_stdlib):
    """Going back multiple times should correctly re-ask earlier questions."""
    frm = make_form({
        "properties": {
            "a": {"type": "string", "title": "A", "default": ""},
            "b": {"type": "string", "title": "B", "default": ""},
            "c": {"type": "string", "title": "C", "default": ""},
        }
    })
    # answer a, answer b, go back to b, go back to a, re-answer a, b, c
    result = render_stdlib(
        frm, ["first_a", "first_b", "<", "<", "final_a", "final_b", "final_c"]
    )
    assert result["a"] == "final_a"
    assert result["b"] == "final_b"
    assert result["c"] == "final_c"


# ---------------------------------------------------------------------------
# Back navigation with different question types
# ---------------------------------------------------------------------------


def test_back_from_boolean_rerenders_previous_string(make_form, render_stdlib):
    """Going back from a boolean question should re-ask the previous string question."""
    frm = make_form({
        "properties": {
            "name": {"type": "string", "title": "Name", "default": ""},
            "confirm": {
                "type": "boolean",
                "title": "Confirm",
                "default": False,
            },
        }
    })
    result = render_stdlib(frm, ["Alice", "<", "Bob", "y"])
    assert result["name"] == "Bob"
    assert result["confirm"] is True


def test_back_from_choice_rerenders_previous_string(make_form, render_stdlib):
    """Going back from a choice question should re-ask the previous string question."""
    frm = make_form({
        "properties": {
            "name": {"type": "string", "title": "Name", "default": ""},
            "role": {
                "type": "string",
                "title": "Role",
                "default": "user",
                "oneOf": [
                    {"const": "user", "title": "User"},
                    {"const": "admin", "title": "Admin"},
                ],
            },
        }
    })
    result = render_stdlib(frm, ["Alice", "<", "Bob", "2"])
    assert result["name"] == "Bob"
    assert result["role"] == "admin"


def test_back_from_multiple_rerenders_previous_string(make_form, render_stdlib):
    """Going back from a multiple question should re-ask the previous string question."""
    frm = make_form({
        "properties": {
            "name": {"type": "string", "title": "Name", "default": ""},
            "tags": {
                "type": "array",
                "title": "Tags",
                "default": ["a"],
                "items": {
                    "oneOf": [
                        {"const": "a", "title": "A"},
                        {"const": "b", "title": "B"},
                    ]
                },
            },
        }
    })
    result = render_stdlib(frm, ["Alice", "<", "Bob", "2"])
    assert result["name"] == "Bob"
    assert result["tags"] == ["b"]


# ---------------------------------------------------------------------------
# Back navigation with conditional questions
# ---------------------------------------------------------------------------


# Note: these tests require oidc_url between provider and name, which can't be
# expressed in schema form (allOf questions always follow properties). Direct
# Form construction preserves the exact question ordering needed.


def _conditional_form() -> form.Form:
    """Build a form with a conditional question between two regular questions."""
    return form.Form(
        title="Test",
        description="",
        questions=[
            form.QuestionChoice(
                key="provider",
                type="string",
                title="Provider",
                description="",
                default="local",
                options=[
                    {"const": "local", "title": "Local"},
                    {"const": "oidc", "title": "OIDC"},
                ],
            ),
            form.Question(
                key="oidc_url",
                type="string",
                title="OIDC URL",
                description="",
                default="",
                condition=[{"key": "provider", "value": "oidc"}],
            ),
            form.Question(
                key="name",
                type="string",
                title="Name",
                description="",
                default="",
            ),
        ],
    )


def test_back_past_gating_question_hides_conditional(render_stdlib):
    """Going back twice from ``name`` through ``oidc_url`` to ``provider`` should hide
    the conditional question when a non-triggering value is re-selected."""
    frm = _conditional_form()
    # Choose "oidc" → answer oidc_url → answer name → go back to name's predecessor
    # (oidc_url) → go back again to provider → choose "local"
    # → oidc_url should be skipped → answer name
    result = render_stdlib(frm, ["2", "https://example.com", "<", "<", "1", "Alice"])
    assert result["provider"] == "local"
    assert "oidc_url" not in result
    assert result["name"] == "Alice"


def test_back_past_gating_question_shows_conditional_on_reselect(render_stdlib):
    """Going back from a non-conditional question to the gating question and
    re-selecting the triggering value should re-ask the conditional question."""
    frm = _conditional_form()
    # Choose "local" (oidc_url skipped) → answer name → go back to provider
    # (history only has "provider") → choose "oidc" → answer oidc_url → answer name
    result = render_stdlib(frm, ["1", "<", "2", "https://oidc.example.com", "Alice"])
    assert result["provider"] == "oidc"
    assert result["oidc_url"] == "https://oidc.example.com"
    assert result["name"] == "Alice"


# ---------------------------------------------------------------------------
# Back hint display
# ---------------------------------------------------------------------------


def test_back_hint_not_shown_for_first_question(make_form):
    """The back hint should not be printed for the first question."""
    frm = make_form({
        "properties": {"a": {"type": "string", "title": "A", "default": ""}}
    })
    with (
        patch("builtins.input", side_effect=[""]),
        patch("builtins.print") as mock_print,
    ):
        StdlibRenderer(frm).render()
    printed = " ".join(str(c) for call in mock_print.call_args_list for c in call.args)
    assert "go back" not in printed


def test_back_hint_shown_for_second_question(make_form):
    """The back hint should be printed when asking the second question."""
    frm = make_form({
        "properties": {
            "a": {"type": "string", "title": "A", "default": ""},
            "b": {"type": "string", "title": "B", "default": ""},
        }
    })
    with (
        patch("builtins.input", side_effect=["a_val", "b_val"]),
        patch("builtins.print") as mock_print,
    ):
        StdlibRenderer(frm).render()
    printed = " ".join(str(c) for call in mock_print.call_args_list for c in call.args)
    assert "go back" in printed


# ---------------------------------------------------------------------------
# Form state after back navigation
# ---------------------------------------------------------------------------


def test_unrecorded_answer_not_in_result(make_form, render_stdlib):
    """An answer cleared by going back should not appear in the final result."""
    frm = make_form({
        "properties": {
            "a": {"type": "string", "title": "A", "default": ""},
            "b": {"type": "string", "title": "B", "default": ""},
        }
    })
    result = render_stdlib(frm, ["first", "<", "second", "final_b"])
    assert result["a"] == "second"
    assert result["b"] == "final_b"
    # The first answer "first" was replaced; only the final values should appear
    assert list(result.keys()) == ["a", "b"]
