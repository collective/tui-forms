from tui_forms import form
from tui_forms.renderer.base import BaseRenderer
from tui_forms.renderer.rich import RichRenderer

import pytest


@pytest.fixture
def renderer_klass() -> type[BaseRenderer]:
    """Return the renderer class being tested."""
    return RichRenderer


# --- String question tests ---


@pytest.mark.parametrize(
    "default,user_input,expected",
    [
        ("hello", "", "hello"),
        ("hello", "world", "world"),
        (None, "", ""),
    ],
)
def test_ask_string(make_form, render, default, user_input, expected):
    """String questions should return user input or fall back to the default."""
    frm = make_form({
        "properties": {"x": {"type": "string", "title": "X", "default": default}}
    })
    assert render(frm, [user_input])["x"] == expected


# --- Boolean question tests ---


@pytest.mark.parametrize("user_input", ["y", "yes"])
def test_boolean_affirmative_returns_true(make_form, render, user_input):
    """Affirmative boolean inputs should return True."""
    frm = make_form({
        "properties": {"b": {"type": "boolean", "title": "B", "default": False}}
    })
    assert render(frm, [user_input])["b"] is True


@pytest.mark.parametrize("user_input", ["n", "no"])
def test_boolean_negative_returns_false(make_form, render, user_input):
    """Negative boolean inputs should return False."""
    frm = make_form({
        "properties": {"b": {"type": "boolean", "title": "B", "default": True}}
    })
    assert render(frm, [user_input])["b"] is False


@pytest.mark.parametrize(
    "default,expected",
    [
        (True, True),
        (False, False),
    ],
)
def test_boolean_empty_uses_default(make_form, render, default, expected):
    """Empty boolean input should fall back to the question default."""
    frm = make_form({
        "properties": {"b": {"type": "boolean", "title": "B", "default": default}}
    })
    assert render(frm, [""])["b"] is expected


def test_boolean_invalid_input_retries(make_form, render):
    """Invalid boolean input should prompt again until a valid answer is given."""
    frm = make_form({
        "properties": {"b": {"type": "boolean", "title": "B", "default": True}}
    })
    assert render(frm, ["maybe", "n"])["b"] is False


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
def test_ask_choice(make_form, render, user_input, expected):
    """Choice questions should return the option matching the entered number or the default."""
    frm = make_form(_CHOICE_SCHEMA)
    assert render(frm, [user_input])["c"] == expected


def test_choice_invalid_input_retries(make_form, render):
    """Invalid choice input should prompt again until a valid answer is given."""
    frm = make_form(_CHOICE_SCHEMA)
    assert render(frm, ["99", "2"])["c"] == "b"


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
def test_ask_multiple(make_form, render, user_input, expected):
    """Multiple questions should return selected options or the default on empty input."""
    frm = make_form(_MULTIPLE_SCHEMA)
    assert render(frm, [user_input])["m"] == expected


def test_multiple_invalid_input_retries(make_form, render):
    """Invalid multiple-choice input should prompt again until a valid answer is given."""
    frm = make_form(_MULTIPLE_SCHEMA)
    assert render(frm, ["99", "1"])["m"] == ["a"]


# --- Validator tests ---


def test_invalid_answer_retries_until_valid(render):
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
    assert render(frm, ["banana", "avocado"])["x"] == "avocado"
