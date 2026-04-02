"""Tests for the tui-forms pytest plugin (tui_forms.fixtures.plugin).

Verifies that the plugin fixtures are discoverable and work correctly
with both stdlib and console-based renderers.
"""

from tui_forms import form
from tui_forms.fixtures._protocols import MakeForm
from tui_forms.fixtures._protocols import MakeQuestions
from tui_forms.fixtures._protocols import RenderForm
from tui_forms.fixtures._protocols import RenderFormCaptureInput
from tui_forms.fixtures.plugin import _extract_prompts
from tui_forms.fixtures.plugin import _has_console
from tui_forms.fixtures.plugin import _render_console
from tui_forms.fixtures.plugin import _render_stdlib
from tui_forms.renderer.base import BaseRenderer
from tui_forms.renderer.cookiecutter import CookiecutterRenderer
from tui_forms.renderer.rich import RichRenderer
from tui_forms.renderer.stdlib import StdlibRenderer
from unittest.mock import MagicMock

import pytest


# ---------------------------------------------------------------------------
# Plugin registration
# ---------------------------------------------------------------------------


def test_plugin_is_registered(pytestconfig):
    """The tui_forms plugin should be registered via the pytest11 entry point."""
    plugin = pytestconfig.pluginmanager.get_plugin("tui_forms")
    assert plugin is not None


# ---------------------------------------------------------------------------
# Protocol conformance
# ---------------------------------------------------------------------------


def test_make_questions_conforms_to_protocol(make_questions):
    """make_questions fixture should conform to MakeQuestions protocol."""
    assert isinstance(make_questions, MakeQuestions)


def test_make_form_conforms_to_protocol(make_form):
    """make_form fixture should conform to MakeForm protocol."""
    assert isinstance(make_form, MakeForm)


def test_render_form_conforms_to_protocol(render_form):
    """render_form fixture should conform to RenderForm protocol."""
    assert isinstance(render_form, RenderForm)


def test_render_form_capture_input_conforms_to_protocol(render_form_capture_input):
    """render_form_capture_input should conform to RenderFormCaptureInput protocol."""
    assert isinstance(render_form_capture_input, RenderFormCaptureInput)


# ---------------------------------------------------------------------------
# _has_console
# ---------------------------------------------------------------------------


def test_has_console_stdlib():
    """StdlibRenderer does not use _console."""
    assert _has_console(StdlibRenderer) is False


def test_has_console_rich():
    """RichRenderer uses _console."""
    assert _has_console(RichRenderer) is True


def test_has_console_cookiecutter():
    """CookiecutterRenderer uses _console."""
    assert _has_console(CookiecutterRenderer) is True


# ---------------------------------------------------------------------------
# _render_stdlib
# ---------------------------------------------------------------------------


def test_render_stdlib_returns_answers_and_mock():
    """_render_stdlib should return (answers_dict, input_mock)."""
    frm = form.Form(
        title="Test",
        description="",
        questions=[
            form.Question(key="x", type="string", title="X", description="", default="")
        ],
    )
    renderer = StdlibRenderer(frm)
    answers, mock = _render_stdlib(renderer, ["hello"])
    assert answers["x"] == "hello"
    assert mock.call_count == 1


def test_render_stdlib_with_confirm():
    """_render_stdlib should support the confirm keyword."""
    frm = form.Form(
        title="Test",
        description="",
        questions=[
            form.Question(key="x", type="string", title="X", description="", default="")
        ],
    )
    renderer = StdlibRenderer(frm)
    answers, _ = _render_stdlib(renderer, ["hi", "y"], confirm=True)
    assert answers["x"] == "hi"


# ---------------------------------------------------------------------------
# _render_console
# ---------------------------------------------------------------------------


def test_render_console_returns_answers_and_mock():
    """_render_console should return (answers_dict, input_mock)."""
    frm = form.Form(
        title="Test",
        description="",
        questions=[
            form.Question(key="x", type="string", title="X", description="", default="")
        ],
    )
    renderer = RichRenderer(frm)
    answers, mock = _render_console(renderer, ["hello"])
    assert answers["x"] == "hello"
    assert mock.call_count >= 1


def test_render_console_with_confirm():
    """_render_console should support the confirm keyword."""
    frm = form.Form(
        title="Test",
        description="",
        questions=[
            form.Question(key="x", type="string", title="X", description="", default="")
        ],
    )
    renderer = RichRenderer(frm)
    answers, _ = _render_console(renderer, ["hi", "y"], confirm=True)
    assert answers["x"] == "hi"


# ---------------------------------------------------------------------------
# _extract_prompts
# ---------------------------------------------------------------------------


def test_extract_prompts_with_args():
    """_extract_prompts should extract arg[0] from each call."""
    mock = MagicMock()
    mock("prompt1")
    mock("prompt2")
    assert _extract_prompts(mock) == ["prompt1", "prompt2"]


def test_extract_prompts_without_args():
    """_extract_prompts should return empty string when call has no args."""
    mock = MagicMock()
    mock()
    assert _extract_prompts(mock) == [""]


def test_extract_prompts_empty():
    """_extract_prompts should return empty list when no calls were made."""
    mock = MagicMock()
    assert _extract_prompts(mock) == []


# ---------------------------------------------------------------------------
# make_questions / make_form fixtures
# ---------------------------------------------------------------------------


def test_make_questions_returns_list(make_questions):
    """make_questions should return a list of BaseQuestion instances."""
    questions = make_questions({
        "properties": {"x": {"type": "string", "default": "hi"}}
    })
    assert len(questions) == 1
    assert isinstance(questions[0], form.BaseQuestion)


def test_make_form_returns_form(make_form):
    """make_form should return a Form instance."""
    frm = make_form({"properties": {"x": {"type": "string", "default": "hi"}}})
    assert isinstance(frm, form.Form)
    assert len(frm.questions) == 1


def test_make_form_root_key(make_form):
    """make_form should support the root_key keyword argument."""
    frm = make_form(
        {"properties": {"x": {"type": "string", "default": "hi"}}},
        root_key="cc",
    )
    assert frm.root_key == "cc"


def test_make_form_uses_schema_title(make_form):
    """make_form should use the title from the schema."""
    frm = make_form({
        "title": "My Form",
        "properties": {"x": {"type": "string", "default": ""}},
    })
    assert frm.title == "My Form"


# ---------------------------------------------------------------------------
# render_form — default renderer (StdlibRenderer)
# ---------------------------------------------------------------------------


def test_render_form_default_renderer(make_form, render_form):
    """render_form should work with the default StdlibRenderer."""
    frm = make_form({"properties": {"name": {"type": "string", "default": "Alice"}}})
    result = render_form(frm, ["Bob"])
    assert result["name"] == "Bob"


def test_render_form_empty_input_uses_default(make_form, render_form):
    """Empty input should fall back to the schema default."""
    frm = make_form({"properties": {"name": {"type": "string", "default": "Alice"}}})
    result = render_form(frm, [""])
    assert result["name"] == "Alice"


def test_render_form_confirm(make_form, render_form):
    """render_form should support the confirm keyword argument."""
    frm = make_form({"properties": {"name": {"type": "string", "default": ""}}})
    result = render_form(frm, ["Alice", "y"], confirm=True)
    assert result["name"] == "Alice"


# ---------------------------------------------------------------------------
# render_form_capture_input — default renderer
# ---------------------------------------------------------------------------


def test_render_form_capture_input_returns_prompts(
    make_form, render_form_capture_input
):
    """render_form_capture_input should return both answers and prompt strings."""
    frm = make_form({
        "properties": {"name": {"type": "string", "title": "Name", "default": "World"}}
    })
    result, prompts = render_form_capture_input(frm, ["Alice"])
    assert result["name"] == "Alice"
    assert len(prompts) == 1
    # StdlibRenderer puts the default in the input() prompt
    assert "World" in prompts[0]


# ---------------------------------------------------------------------------
# render_form — Rich renderer
# ---------------------------------------------------------------------------


class TestRichRenderer:
    """Tests verifying render_form works with RichRenderer."""

    @pytest.fixture
    def renderer_klass(self) -> type[BaseRenderer]:
        """Override to use RichRenderer."""
        return RichRenderer

    def test_render_form_string(self, make_form, render_form):
        """RichRenderer should handle a string question."""
        frm = make_form({"properties": {"x": {"type": "string", "default": "a"}}})
        assert render_form(frm, ["b"])["x"] == "b"

    def test_render_form_capture_input(self, make_form, render_form_capture_input):
        """RichRenderer capture should return prompt strings."""
        frm = make_form({
            "properties": {"x": {"type": "string", "title": "X", "default": ""}}
        })
        result, prompts = render_form_capture_input(frm, ["val"])
        assert result["x"] == "val"
        assert len(prompts) >= 1

    def test_render_form_confirm(self, make_form, render_form):
        """RichRenderer should support confirm mode."""
        frm = make_form({"properties": {"x": {"type": "string", "default": ""}}})
        result = render_form(frm, ["hi", "y"], confirm=True)
        assert result["x"] == "hi"


# ---------------------------------------------------------------------------
# render_form — Cookiecutter renderer
# ---------------------------------------------------------------------------


class TestCookiecutterRenderer:
    """Tests verifying render_form works with CookiecutterRenderer."""

    @pytest.fixture
    def renderer_klass(self) -> type[BaseRenderer]:
        """Override to use CookiecutterRenderer."""
        return CookiecutterRenderer

    def test_render_form_string(self, make_form, render_form):
        """CookiecutterRenderer should handle a string question."""
        frm = make_form({"properties": {"x": {"type": "string", "default": "a"}}})
        assert render_form(frm, ["b"])["x"] == "b"

    def test_render_form_capture_input(self, make_form, render_form_capture_input):
        """CookiecutterRenderer capture should return prompt strings."""
        frm = make_form({
            "properties": {"x": {"type": "string", "title": "X", "default": ""}}
        })
        result, prompts = render_form_capture_input(frm, ["val"])
        assert result["x"] == "val"
        assert len(prompts) >= 1
