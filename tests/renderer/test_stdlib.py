from tui_forms import form
from tui_forms.renderer.stdlib import StdlibRenderer
from typing import Any
from unittest.mock import patch

import pytest


@pytest.fixture
def render():
    """Return a factory that renders a form with a pre-set sequence of input() return values."""

    def factory(frm: form.Form, inputs: list[str]) -> dict[str, Any]:
        """Render a form using patched input() calls."""
        with patch("builtins.input", side_effect=inputs), patch("builtins.print"):
            return StdlibRenderer(frm).render()

    return factory


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
    frm = make_form(
        form.Question(
            key="x", type="string", title="X", description="", default=default
        )
    )
    assert render(frm, [user_input])["x"] == expected


# --- Boolean question tests ---


@pytest.mark.parametrize("user_input", ["y", "yes"])
def test_boolean_affirmative_returns_true(make_form, render, user_input):
    """Affirmative boolean inputs should return True."""
    frm = make_form(
        form.QuestionBoolean(
            key="b", type="boolean", title="B", description="", default=False
        )
    )
    assert render(frm, [user_input])["b"] is True


@pytest.mark.parametrize("user_input", ["n", "no"])
def test_boolean_negative_returns_false(make_form, render, user_input):
    """Negative boolean inputs should return False."""
    frm = make_form(
        form.QuestionBoolean(
            key="b", type="boolean", title="B", description="", default=True
        )
    )
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
    frm = make_form(
        form.QuestionBoolean(
            key="b", type="boolean", title="B", description="", default=default
        )
    )
    assert render(frm, [""])["b"] is expected


def test_boolean_invalid_input_retries(make_form, render):
    """Invalid boolean input should prompt again until a valid answer is given."""
    frm = make_form(
        form.QuestionBoolean(
            key="b", type="boolean", title="B", description="", default=True
        )
    )
    assert render(frm, ["maybe", "n"])["b"] is False


# --- Choice question tests ---


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
    frm = make_form(
        form.QuestionChoice(
            key="c",
            type="string",
            title="C",
            description="",
            default="a",
            options=[{"const": "a", "title": "A"}, {"const": "b", "title": "B"}],
        )
    )
    assert render(frm, [user_input])["c"] == expected


def test_choice_invalid_input_retries(make_form, render):
    """Invalid choice input should prompt again until a valid answer is given."""
    frm = make_form(
        form.QuestionChoice(
            key="c",
            type="string",
            title="C",
            description="",
            default="a",
            options=[{"const": "a", "title": "A"}, {"const": "b", "title": "B"}],
        )
    )
    assert render(frm, ["99", "2"])["c"] == "b"


# --- Multiple question tests ---


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
    frm = make_form(
        form.QuestionMultiple(
            key="m",
            type="array",
            title="M",
            description="",
            default=["a"],
            options=[{"const": "a", "title": "A"}, {"const": "b", "title": "B"}],
        )
    )
    assert render(frm, [user_input])["m"] == expected


def test_multiple_invalid_input_retries(make_form, render):
    """Invalid multiple-choice input should prompt again until a valid answer is given."""
    frm = make_form(
        form.QuestionMultiple(
            key="m",
            type="array",
            title="M",
            description="",
            default=["a"],
            options=[{"const": "a", "title": "A"}, {"const": "b", "title": "B"}],
        )
    )
    assert render(frm, ["99", "1"])["m"] == ["a"]


# --- Hidden question tests ---


def test_constant_question_value(make_form, render):
    """A QuestionConstant should always return its raw default value."""
    frm = make_form(
        form.QuestionConstant(
            key="c", type="string", title="C", description="", default="fixed"
        )
    )
    assert render(frm, [])["c"] == "fixed"


def test_computed_question_uses_answers(make_form, render):
    """A QuestionComputed should render its default template against prior answers."""
    frm = make_form(
        form.Question(
            key="name", type="string", title="Name", description="", default="World"
        ),
        form.QuestionComputed(
            key="greeting",
            type="string",
            title="Greeting",
            description="",
            default="Hello {{ name }}!",
        ),
    )
    assert render(frm, ["Alice"])["greeting"] == "Hello Alice!"


def test_hidden_questions_not_in_user_inputs(make_form, render):
    """Hidden questions should not consume any input() calls."""
    frm = make_form(
        form.Question(
            key="name", type="string", title="Name", description="", default="World"
        ),
        form.QuestionConstant(
            key="version",
            type="string",
            title="Version",
            description="",
            default="1.0",
        ),
    )
    # Only one input() call expected (for "name"), not for "version"
    answers = render(frm, ["Alice"])
    assert answers["name"] == "Alice"
    assert answers["version"] == "1.0"


# --- Condition tests ---


def test_condition_satisfied_question_is_asked(make_form, render):
    """A conditional question should be asked when the condition is satisfied."""
    frm = make_form(
        form.QuestionChoice(
            key="provider",
            type="string",
            title="Provider",
            description="",
            default="a",
            options=[{"const": "a", "title": "A"}, {"const": "b", "title": "B"}],
        ),
        form.Question(
            key="secret",
            type="string",
            title="Secret",
            description="",
            default="",
            condition={"key": "provider", "value": "b"},
        ),
    )
    assert render(frm, ["2", "mypassword"])["secret"] == "mypassword"


def test_condition_not_satisfied_question_skipped(make_form, render):
    """A conditional question should be skipped when the condition is not satisfied."""
    frm = make_form(
        form.QuestionChoice(
            key="provider",
            type="string",
            title="Provider",
            description="",
            default="a",
            options=[{"const": "a", "title": "A"}, {"const": "b", "title": "B"}],
        ),
        form.Question(
            key="secret",
            type="string",
            title="Secret",
            description="",
            default="",
            condition={"key": "provider", "value": "b"},
        ),
    )
    assert "secret" not in render(frm, [""])


def test_hidden_condition_satisfied_is_computed(make_form, render):
    """A hidden conditional question should be included when the condition is satisfied."""
    frm = make_form(
        form.QuestionChoice(
            key="mode",
            type="string",
            title="Mode",
            description="",
            default="full",
            options=[
                {"const": "full", "title": "Full"},
                {"const": "lite", "title": "Lite"},
            ],
        ),
        form.QuestionConstant(
            key="flag",
            type="string",
            title="Flag",
            description="",
            default="enabled",
            condition={"key": "mode", "value": "full"},
        ),
    )
    assert render(frm, [""])["flag"] == "enabled"


def test_hidden_condition_not_satisfied_skipped(make_form, render):
    """A hidden conditional question should be skipped when the condition is not satisfied."""
    frm = make_form(
        form.QuestionChoice(
            key="mode",
            type="string",
            title="Mode",
            description="",
            default="full",
            options=[
                {"const": "full", "title": "Full"},
                {"const": "lite", "title": "Lite"},
            ],
        ),
        form.QuestionConstant(
            key="flag",
            type="string",
            title="Flag",
            description="",
            default="enabled",
            condition={"key": "mode", "value": "lite"},
        ),
    )
    assert "flag" not in render(frm, [""])


# --- Object question tests ---


def test_subquestions_are_asked(make_form, render):
    """Subquestions of an object question should all be asked."""
    frm = make_form(
        form.Question(
            key="obj",
            type="object",
            title="Object",
            description="",
            default=None,
            subquestions=[
                form.Question(
                    key="sub1",
                    type="string",
                    title="Sub1",
                    description="",
                    default="a",
                ),
                form.Question(
                    key="sub2",
                    type="string",
                    title="Sub2",
                    description="",
                    default="b",
                ),
            ],
        )
    )
    answers = render(frm, ["x", "y"])
    assert answers["sub1"] == "x"
    assert answers["sub2"] == "y"


def test_object_parent_key_not_in_answers(make_form, render):
    """The parent key of an object question should not appear in the answers dict."""
    frm = make_form(
        form.Question(
            key="obj",
            type="object",
            title="Object",
            description="",
            default=None,
            subquestions=[
                form.Question(
                    key="sub1",
                    type="string",
                    title="Sub1",
                    description="",
                    default="a",
                ),
            ],
        )
    )
    answers = render(frm, [""])
    assert "obj" not in answers
    assert "sub1" in answers


# --- Validator tests ---


def test_valid_answer_is_accepted(make_form, render):
    """A passing validator should accept the answer without retrying."""
    frm = make_form(
        form.Question(
            key="x",
            type="string",
            title="X",
            description="",
            default="",
            validator=lambda v: v.startswith("a"),
        )
    )
    assert render(frm, ["apple"])["x"] == "apple"


def test_invalid_answer_retries_until_valid(make_form, render):
    """A failing validator should cause the question to be re-asked."""
    frm = make_form(
        form.Question(
            key="x",
            type="string",
            title="X",
            description="",
            default="",
            validator=lambda v: v.startswith("a"),
        )
    )
    assert render(frm, ["banana", "avocado"])["x"] == "avocado"


def test_no_validator_accepts_any_answer(make_form, render):
    """Without a validator, any answer should be accepted."""
    frm = make_form(
        form.Question(
            key="x",
            type="string",
            title="X",
            description="",
            default="",
            validator=None,
        )
    )
    assert render(frm, ["anything"])["x"] == "anything"


# ---------------------------------------------------------------------------
# _user_answers
# ---------------------------------------------------------------------------


def test_interactive_renderer_populates_user_answers(make_form):
    """Interactive renderers mark every user-facing question key as user-provided."""
    frm = make_form(
        form.Question(key="a", type="string", title="A", description="", default=""),
        form.Question(key="b", type="string", title="B", description="", default=""),
    )
    with patch("builtins.input", side_effect=["x", "y"]), patch("builtins.print"):
        StdlibRenderer(frm).render()
    assert frm._user_answers == {"a", "b"}


def test_hidden_field_not_in_user_answers(make_form):
    """Hidden computed fields are never added to _user_answers."""
    frm = make_form(
        form.Question(
            key="name", type="string", title="Name", description="", default=""
        ),
        form.QuestionComputed(
            key="slug", type="string", title="", description="", default="{{ name }}"
        ),
    )
    with patch("builtins.input", side_effect=["alice"]), patch("builtins.print"):
        StdlibRenderer(frm).render()
    assert "name" in frm._user_answers
    assert "slug" not in frm._user_answers
