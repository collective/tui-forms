from tui_forms import form
from tui_forms.renderer.base import BaseRenderer
from tui_forms.renderer.noinput import NoInputRenderer


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _replay(frm: form.Form, initial_answers=None) -> dict:
    return NoInputRenderer(frm).render(initial_answers=initial_answers)


def _form(*questions: form.BaseQuestion, root_key: str = "") -> form.Form:
    return form.Form(
        title="Test", description="", questions=list(questions), root_key=root_key
    )


# ---------------------------------------------------------------------------
# String questions
# ---------------------------------------------------------------------------


def test_string_uses_schema_default():
    """String question with no pre-populated answer returns the schema default."""
    frm = _form(
        form.Question(
            key="name", type="string", title="Name", description="", default="Alice"
        )
    )
    assert _replay(frm)["name"] == "Alice"


def test_string_uses_prepopulated_answer():
    """Pre-populated answer takes priority over the schema default."""
    frm = _form(
        form.Question(
            key="name", type="string", title="Name", description="", default="Alice"
        )
    )
    assert _replay(frm, {"name": "Bob"})["name"] == "Bob"


def test_string_none_default_returns_empty_string():
    """String question with no default and no pre-populated answer returns ''."""
    frm = _form(
        form.Question(key="x", type="string", title="X", description="", default=None)
    )
    assert _replay(frm)["x"] == ""


# ---------------------------------------------------------------------------
# Boolean questions
# ---------------------------------------------------------------------------


def test_boolean_uses_schema_default():
    frm = _form(
        form.QuestionBoolean(
            key="flag", type="boolean", title="Flag", description="", default=True
        )
    )
    assert _replay(frm)["flag"] is True


def test_boolean_uses_prepopulated_answer():
    frm = _form(
        form.QuestionBoolean(
            key="flag", type="boolean", title="Flag", description="", default=True
        )
    )
    assert _replay(frm, {"flag": False})["flag"] is False


# ---------------------------------------------------------------------------
# Choice questions
# ---------------------------------------------------------------------------


def test_choice_uses_schema_default():
    frm = _form(
        form.QuestionChoice(
            key="env",
            type="string",
            title="Env",
            description="",
            default="prod",
            options=[
                {"const": "dev", "title": "Dev"},
                {"const": "prod", "title": "Prod"},
            ],
        )
    )
    assert _replay(frm)["env"] == "prod"


def test_choice_uses_prepopulated_answer():
    frm = _form(
        form.QuestionChoice(
            key="env",
            type="string",
            title="Env",
            description="",
            default="prod",
            options=[
                {"const": "dev", "title": "Dev"},
                {"const": "prod", "title": "Prod"},
            ],
        )
    )
    assert _replay(frm, {"env": "dev"})["env"] == "dev"


# ---------------------------------------------------------------------------
# Multiple-choice questions
# ---------------------------------------------------------------------------


def test_multiple_uses_schema_default():
    frm = _form(
        form.QuestionMultiple(
            key="tags",
            type="array",
            title="Tags",
            description="",
            default=["a"],
            options=[{"const": "a", "title": "A"}, {"const": "b", "title": "B"}],
        )
    )
    assert _replay(frm)["tags"] == ["a"]


def test_multiple_uses_prepopulated_answer():
    frm = _form(
        form.QuestionMultiple(
            key="tags",
            type="array",
            title="Tags",
            description="",
            default=["a"],
            options=[{"const": "a", "title": "A"}, {"const": "b", "title": "B"}],
        )
    )
    assert _replay(frm, {"tags": ["a", "b"]})["tags"] == ["a", "b"]


# ---------------------------------------------------------------------------
# root_key
# ---------------------------------------------------------------------------


def test_root_key_nesting():
    """With root_key set, answers are nested under that key."""
    frm = _form(
        form.Question(
            key="name", type="string", title="Name", description="", default="Alice"
        ),
        root_key="cc",
    )
    result = _replay(frm)
    assert result == {"cc": {"name": "Alice"}}


def test_root_key_with_prepopulated_answers():
    """Pre-populated answers nested under root_key are respected."""
    frm = _form(
        form.Question(
            key="name", type="string", title="Name", description="", default="Alice"
        ),
        root_key="cc",
    )
    result = _replay(frm, {"cc": {"name": "Bob"}})
    assert result == {"cc": {"name": "Bob"}}


# ---------------------------------------------------------------------------
# Hidden fields
# ---------------------------------------------------------------------------


def test_computed_field_is_resolved():
    """Computed hidden fields are resolved after user-facing questions."""
    frm = _form(
        form.Question(
            key="first", type="string", title="First", description="", default="Hello"
        ),
        form.QuestionComputed(
            key="greeting",
            type="string",
            title="",
            description="",
            default="{{ first }} world",
        ),
    )
    result = _replay(frm)
    assert result["greeting"] == "Hello world"


def test_constant_field_is_resolved():
    """Constant hidden fields always return their raw value."""
    frm = _form(
        form.QuestionConstant(
            key="version", type="string", title="", description="", default="1.0"
        )
    )
    assert _replay(frm)["version"] == "1.0"


# ---------------------------------------------------------------------------
# Full round-trip
# ---------------------------------------------------------------------------


def test_round_trip():
    """A full replay of a previous render() output returns the same answers."""
    frm = _form(
        form.Question(
            key="project",
            type="string",
            title="Project",
            description="",
            default="myapp",
        ),
        form.QuestionBoolean(
            key="docs", type="boolean", title="Docs?", description="", default=True
        ),
        form.QuestionComputed(
            key="slug",
            type="string",
            title="",
            description="",
            default="{{ project }}-slug",
        ),
    )
    previous = {"project": "mylib", "docs": False, "slug": "mylib-slug"}
    result = _replay(frm, previous)
    assert result["project"] == "mylib"
    assert result["docs"] is False
    assert result["slug"] == "mylib-slug"


# ---------------------------------------------------------------------------
# Constructor compatibility
# ---------------------------------------------------------------------------


def test_constructor_is_compatible_with_base_renderer():
    """NoInputRenderer(frm) requires only frm, matching the BaseRenderer contract."""
    frm = _form(
        form.Question(key="x", type="string", title="X", description="", default="v")
    )
    renderer = NoInputRenderer(frm)
    assert isinstance(renderer, BaseRenderer)


def test_render_with_no_args_uses_schema_defaults():
    """render() with no arguments falls back to schema defaults, returning valid output."""
    frm = _form(
        form.Question(
            key="name",
            type="string",
            title="Name",
            description="",
            default="default-name",
        )
    )
    result = NoInputRenderer(frm).render()
    assert result["name"] == "default-name"
