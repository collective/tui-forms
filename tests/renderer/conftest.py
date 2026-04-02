from tui_forms import form
from tui_forms.parser import jsonschema_to_form
from tui_forms.renderer.base import BaseRenderer
from tui_forms.renderer.stdlib import StdlibRenderer
from typing import Any
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest


@pytest.fixture
def renderer_klass() -> type[BaseRenderer]:
    """Return the renderer class being tested."""
    return StdlibRenderer


@pytest.fixture
def make_questions():
    """Return a factory that parses a JSONSchema dict into a list of questions."""

    def factory(schema: dict[str, Any]) -> list[form.BaseQuestion]:
        """Parse a JSONSchema and return the resulting questions."""
        parsed = jsonschema_to_form(schema)
        return parsed.questions

    return factory


@pytest.fixture
def make_form(make_questions):
    """Return a factory that builds a Form from a JSONSchema dict."""

    def factory(schema: dict[str, Any], *, root_key: str = "") -> form.Form:
        """Build a Form from a JSONSchema dict."""
        questions = make_questions(schema)
        return form.Form(
            title=schema.get("title", "Test"),
            description=schema.get("description", ""),
            questions=questions,
            root_key=root_key,
        )

    return factory


@pytest.fixture
def render(renderer_klass):
    """Return a factory that renders a form with a mocked Rich console."""

    def factory(frm: form.Form, inputs: list[str]) -> dict[str, Any]:
        """Render a form using a mock console with preset input() return values."""
        renderer = renderer_klass(frm)
        renderer._console = MagicMock()
        renderer._console.input.side_effect = inputs
        return renderer.render()

    return factory


@pytest.fixture
def render_stdlib():
    """Return a factory that renders a form via StdlibRenderer with patched input/print."""

    def factory(
        frm: form.Form, inputs: list[str], *, confirm: bool = False
    ) -> dict[str, Any]:
        """Render a form with preset stdin values and suppressed output."""
        with patch("builtins.input", side_effect=inputs), patch("builtins.print"):
            return StdlibRenderer(frm).render(confirm=confirm)

    return factory


@pytest.fixture
def render_stdlib_capture_input():
    """Return a factory that renders via StdlibRenderer and captures input() prompts."""

    def factory(frm: form.Form, inputs: list[str]) -> tuple[dict[str, Any], list[str]]:
        """Render a form and return (answers, list_of_input_prompts)."""
        with (
            patch("builtins.input", side_effect=inputs) as mock_input,
            patch("builtins.print"),
        ):
            result = StdlibRenderer(frm).render()
        prompts = [str(c.args[0]) if c.args else "" for c in mock_input.call_args_list]
        return result, prompts

    return factory
