"""Tests for issue #16: go-back should retain user-entered values as defaults.

When the user goes back to a previous question, the answer they entered before
should be shown as the default — not the original schema default.

See: https://github.com/collective/tui-forms/issues/16
     https://github.com/plone/cookieplone/issues/159
"""

from tui_forms import form
from tui_forms.renderer.stdlib import StdlibRenderer
from typing import Any
from unittest.mock import patch


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_form(*questions: form.BaseQuestion) -> form.Form:
    """Build a minimal Form from positional questions."""
    return form.Form(title="Test", description="", questions=list(questions))


def render_stdlib(frm: form.Form, inputs: list[str]) -> dict[str, Any]:
    """Render *frm* with a patched ``input()`` that returns *inputs* in order."""
    with patch("builtins.input", side_effect=inputs), patch("builtins.print"):
        return StdlibRenderer(frm).render()


def render_stdlib_capture_input(
    frm: form.Form, inputs: list[str]
) -> tuple[dict[str, Any], list[str]]:
    """Render *frm* and return (answers, list_of_input_prompts)."""
    with (
        patch("builtins.input", side_effect=inputs) as mock_input,
        patch("builtins.print"),
    ):
        result = StdlibRenderer(frm).render()
    prompts = [str(c.args[0]) if c.args else "" for c in mock_input.call_args_list]
    return result, prompts


# ---------------------------------------------------------------------------
# Go-back retains user-entered string values
# ---------------------------------------------------------------------------


def test_go_back_shows_previous_answer_as_default():
    """After going back, the prompt should show the user's previous answer,
    not the schema default."""
    frm = make_form(
        form.Question(
            key="version",
            type="string",
            title="Version",
            description="",
            default="1.0.0",
        ),
        form.Question(
            key="name", type="string", title="Name", description="", default=""
        ),
    )
    # Answer "2.0.0", advance, go back, press Enter (accept previous), answer name
    result, prompts = render_stdlib_capture_input(frm, ["2.0.0", "<", "", "Alice"])
    assert result["version"] == "2.0.0"
    # The first prompt for version shows schema default [1.0.0]
    assert "[1.0.0]" in prompts[0]
    # The second prompt for version (after go-back) should show [2.0.0]
    version_prompts = [p for p in prompts if "2.0.0" in p or "1.0.0" in p]
    assert any("2.0.0" in p for p in version_prompts), (
        f"Expected user's previous answer '2.0.0' in prompts, got: {version_prompts}"
    )


def test_go_back_enter_accepts_previous_answer():
    """Pressing Enter after going back should accept the user's previous answer."""
    frm = make_form(
        form.Question(
            key="version",
            type="string",
            title="Version",
            description="",
            default="1.0.0",
        ),
        form.Question(
            key="name", type="string", title="Name", description="", default=""
        ),
    )
    # Answer "custom", advance, go back, press Enter, answer name
    result = render_stdlib(frm, ["custom", "<", "", "Alice"])
    assert result["version"] == "custom"
    assert result["name"] == "Alice"


def test_go_back_can_change_previous_answer():
    """Going back and typing a new value should replace the previous answer."""
    frm = make_form(
        form.Question(
            key="version",
            type="string",
            title="Version",
            description="",
            default="1.0.0",
        ),
        form.Question(
            key="name", type="string", title="Name", description="", default=""
        ),
    )
    # Answer "2.0.0", advance, go back, type "3.0.0", answer name
    result = render_stdlib(frm, ["2.0.0", "<", "3.0.0", "Alice"])
    assert result["version"] == "3.0.0"
    assert result["name"] == "Alice"


# ---------------------------------------------------------------------------
# Go-back retains choice values
# ---------------------------------------------------------------------------


def test_go_back_retains_choice_value():
    """After going back, a choice question should show the previous selection
    as the default."""
    frm = make_form(
        form.QuestionChoice(
            key="license",
            type="string",
            title="License",
            description="",
            default="mit",
            options=[
                {"const": "mit", "title": "MIT"},
                {"const": "gpl", "title": "GPL"},
                {"const": "apache", "title": "Apache"},
            ],
        ),
        form.Question(
            key="name", type="string", title="Name", description="", default=""
        ),
    )
    # Select GPL (2), advance, go back, press Enter (accept GPL), answer name
    result = render_stdlib(frm, ["2", "<", "", "Alice"])
    assert result["license"] == "gpl"
    assert result["name"] == "Alice"


# ---------------------------------------------------------------------------
# Go-back retains boolean values
# ---------------------------------------------------------------------------


def test_go_back_retains_boolean_value():
    """After going back, a boolean question should keep the user's previous answer."""
    frm = make_form(
        form.QuestionBoolean(
            key="use_docker",
            type="boolean",
            title="Use Docker?",
            description="",
            default=False,
        ),
        form.Question(
            key="name", type="string", title="Name", description="", default=""
        ),
    )
    # Answer "y" (True), advance, go back, press Enter (accept True), answer name
    result = render_stdlib(frm, ["y", "<", "", "Alice"])
    assert result["use_docker"] is True
    assert result["name"] == "Alice"


# ---------------------------------------------------------------------------
# Go-back retains multiple-choice values
# ---------------------------------------------------------------------------


def test_go_back_retains_multiple_values():
    """After going back, a multiple-choice question should keep previous selections."""
    frm = make_form(
        form.QuestionMultiple(
            key="extras",
            type="array",
            title="Extras",
            description="",
            default=["a"],
            options=[
                {"const": "a", "title": "Alpha"},
                {"const": "b", "title": "Beta"},
                {"const": "c", "title": "Charlie"},
            ],
        ),
        form.Question(
            key="name", type="string", title="Name", description="", default=""
        ),
    )
    # Select Beta,Charlie (2,3), advance, go back, press Enter (accept previous), answer name
    result = render_stdlib(frm, ["2,3", "<", "", "Alice"])
    assert result["extras"] == ["b", "c"]
    assert result["name"] == "Alice"


# ---------------------------------------------------------------------------
# Go-back with conditional questions
# ---------------------------------------------------------------------------


def test_go_back_retains_answer_for_conditional_evaluation():
    """The gating answer should remain so conditional questions stay visible
    after going back and re-accepting the same gating value."""
    frm = make_form(
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
            key="name", type="string", title="Name", description="", default=""
        ),
    )
    # Choose "oidc" (2), answer url, go back to url, press Enter (keep url),
    # answer name
    result = render_stdlib(frm, ["2", "https://id.example.com", "<", "", "Alice"])
    assert result["provider"] == "oidc"
    assert result["oidc_url"] == "https://id.example.com"
    assert result["name"] == "Alice"


# ---------------------------------------------------------------------------
# Three-question reproduction from issue description
# ---------------------------------------------------------------------------


def test_issue_16_reproduction():
    """Exact reproduction scenario from the issue description."""
    frm = make_form(
        form.Question(
            key="title",
            type="string",
            title="Project Title",
            description="",
            default="My Project",
        ),
        form.Question(
            key="version",
            type="string",
            title="Version",
            description="",
            default="1.0.0",
        ),
        form.Question(
            key="description",
            type="string",
            title="Description",
            description="",
            default="",
        ),
    )
    # Answer title, answer version="custom-version", go back from description,
    # press Enter on version (should keep "custom-version"), answer description
    result = render_stdlib(
        frm, ["My Project", "custom-version", "<", "", "A description"]
    )
    assert result["title"] == "My Project"
    assert result["version"] == "custom-version"
    assert result["description"] == "A description"
