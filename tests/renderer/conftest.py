from tui_forms import form
from tui_forms.renderer.base import BaseRenderer
from tui_forms.renderer.stdlib import StdlibRenderer
from typing import Any
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def renderer_klass() -> type[BaseRenderer]:
    """Return the renderer class being tested."""
    return StdlibRenderer


@pytest.fixture
def make_form():
    """Return a factory that builds a minimal Form from positional question arguments."""

    def factory(*questions: form.BaseQuestion) -> form.Form:
        """Build a Form from positional question arguments."""
        return form.Form(title="Test", description="", questions=list(questions))

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
