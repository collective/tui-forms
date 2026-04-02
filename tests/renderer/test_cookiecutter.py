from tui_forms import form
from tui_forms.renderer.base import BaseRenderer
from tui_forms.renderer.cookiecutter import CookiecutterRenderer

import pytest


@pytest.fixture
def renderer_klass() -> type[BaseRenderer]:
    """Return the renderer class being tested."""
    return CookiecutterRenderer


# --- String question tests ---


@pytest.mark.parametrize(
    "default,user_input,expected",
    [
        ("hello", "", "hello"),
        ("hello", "world", "world"),
        (None, "", ""),
    ],
)
def test_ask_string(make_form, render_form, default, user_input, expected):
    """String questions should return user input or fall back to the default."""
    frm = make_form({
        "properties": {"x": {"type": "string", "title": "X", "default": default}}
    })
    assert render_form(frm, [user_input])["x"] == expected


# --- Boolean question tests ---


@pytest.mark.parametrize("user_input", ["y", "yes"])
def test_boolean_affirmative_returns_true(make_form, render_form, user_input):
    """Affirmative boolean inputs should return True."""
    frm = make_form({
        "properties": {"b": {"type": "boolean", "title": "B", "default": False}}
    })
    assert render_form(frm, [user_input])["b"] is True


@pytest.mark.parametrize("user_input", ["n", "no"])
def test_boolean_negative_returns_false(make_form, render_form, user_input):
    """Negative boolean inputs should return False."""
    frm = make_form({
        "properties": {"b": {"type": "boolean", "title": "B", "default": True}}
    })
    assert render_form(frm, [user_input])["b"] is False


@pytest.mark.parametrize(
    "default,expected",
    [
        (True, True),
        (False, False),
    ],
)
def test_boolean_empty_uses_default(make_form, render_form, default, expected):
    """Empty boolean input should fall back to the question default."""
    frm = make_form({
        "properties": {"b": {"type": "boolean", "title": "B", "default": default}}
    })
    assert render_form(frm, [""])["b"] is expected


def test_boolean_invalid_input_retries(make_form, render_form):
    """Invalid boolean input should prompt again until a valid answer is given."""
    frm = make_form({
        "properties": {"b": {"type": "boolean", "title": "B", "default": True}}
    })
    assert render_form(frm, ["maybe", "n"])["b"] is False


def test_boolean_invalid_input_prints_error(make_form, render_form):
    """Invalid boolean input should display an error message before re-prompting."""
    frm = make_form({
        "properties": {"b": {"type": "boolean", "title": "B", "default": True}}
    })
    renderer = CookiecutterRenderer(frm)
    from unittest.mock import MagicMock

    renderer._console = MagicMock()
    renderer._console.input.side_effect = ["oops", "y"]
    renderer.render()
    printed = " ".join(
        str(a) for call in renderer._console.print.call_args_list for a in call.args
    )
    assert "y or n" in printed


# --- Choice question tests ---


_CHOICE_SCHEMA = {
    "properties": {
        "c": {
            "type": "string",
            "title": "C",
            "default": "a",
            "oneOf": [{"const": "a", "title": "A"}, {"const": "b", "title": "B"}],
        }
    }
}


@pytest.mark.parametrize(
    "user_input,expected",
    [
        ("", "a"),
        ("1", "a"),
        ("2", "b"),
    ],
)
def test_ask_choice(make_form, render_form, user_input, expected):
    """Choice questions should return the option matching the entered number or the default."""
    frm = make_form(_CHOICE_SCHEMA)
    assert render_form(frm, [user_input])["c"] == expected


def test_choice_invalid_input_retries(make_form, render_form):
    """Invalid choice input should prompt again until a valid answer is given."""
    frm = make_form(_CHOICE_SCHEMA)
    assert render_form(frm, ["99", "2"])["c"] == "b"


def test_choice_invalid_input_prints_error(make_form):
    """Invalid choice input should display an error message before re-prompting."""
    frm = make_form(_CHOICE_SCHEMA)
    from unittest.mock import MagicMock

    renderer = CookiecutterRenderer(frm)
    renderer._console = MagicMock()
    renderer._console.input.side_effect = ["99", "1"]
    renderer.render()
    printed = " ".join(
        str(a) for call in renderer._console.print.call_args_list for a in call.args
    )
    assert "1 and 2" in printed


# --- Multiple question tests ---


_MULTIPLE_SCHEMA = {
    "properties": {
        "m": {
            "type": "array",
            "title": "M",
            "default": ["a"],
            "items": {
                "oneOf": [
                    {"const": "a", "title": "A"},
                    {"const": "b", "title": "B"},
                ]
            },
        }
    }
}


@pytest.mark.parametrize(
    "user_input,expected",
    [
        ("", ["a"]),
        ("1, 2", ["a", "b"]),
        ("2", ["b"]),
    ],
)
def test_ask_multiple(make_form, render_form, user_input, expected):
    """Multiple questions should return selected options or the default on empty input."""
    frm = make_form(_MULTIPLE_SCHEMA)
    assert render_form(frm, [user_input])["m"] == expected


def test_multiple_invalid_input_retries(make_form, render_form):
    """Invalid multiple-choice input should prompt again until a valid answer is given."""
    frm = make_form(_MULTIPLE_SCHEMA)
    assert render_form(frm, ["99", "1"])["m"] == ["a"]


def test_multiple_invalid_input_prints_error(make_form):
    """Invalid multiple-choice input should display an error message before re-prompting."""
    frm = make_form(_MULTIPLE_SCHEMA)
    from unittest.mock import MagicMock

    renderer = CookiecutterRenderer(frm)
    renderer._console = MagicMock()
    renderer._console.input.side_effect = ["99", "1"]
    renderer.render()
    printed = " ".join(
        str(a) for call in renderer._console.print.call_args_list for a in call.args
    )
    assert "1 and 2" in printed


# --- Validator tests ---


def test_invalid_answer_retries_until_valid(render_form):
    """A failing validator should cause the question to be re-asked."""
    frm = form.Form(
        title="Test",
        description="",
        questions=[
            form.Question(
                key="x",
                type="string",
                title="X",
                description="",
                default="",
                validator=lambda v: v.startswith("a"),
            )
        ],
    )
    assert render_form(frm, ["banana", "avocado"])["x"] == "avocado"
