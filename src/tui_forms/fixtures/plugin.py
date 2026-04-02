"""pytest plugin providing test fixtures for tui-forms consumers.

Register via the ``pytest11`` entry point so that any project with
``tui-forms[test]`` in its dev dependencies gets these fixtures
automatically — no manual conftest imports needed.
"""

from tui_forms import form
from tui_forms.fixtures._protocols import MakeForm
from tui_forms.fixtures._protocols import MakeQuestions
from tui_forms.fixtures._protocols import RenderForm
from tui_forms.fixtures._protocols import RenderFormCaptureInput
from tui_forms.parser import jsonschema_to_form
from tui_forms.renderer.base import BaseRenderer
from tui_forms.renderer.stdlib import StdlibRenderer
from typing import Any
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest


@pytest.fixture
def renderer_klass() -> type[BaseRenderer]:
    """Return the renderer class used by ``render_form``.

    Defaults to :class:`StdlibRenderer`.  Override this fixture in your
    own ``conftest.py`` to test against a different renderer::

        @pytest.fixture
        def renderer_klass():
            from tui_forms.renderer.rich import RichRenderer
            return RichRenderer
    """
    return StdlibRenderer


@pytest.fixture
def make_questions() -> MakeQuestions:
    """Return a factory that parses a JSONSchema dict into a list of questions."""

    def factory(schema: dict[str, Any]) -> list[form.BaseQuestion]:
        """Parse a JSONSchema and return the resulting questions."""
        parsed = jsonschema_to_form(schema)
        return parsed.questions

    return factory


@pytest.fixture
def make_form(make_questions: MakeQuestions) -> MakeForm:
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


def _has_console(renderer_klass: type[BaseRenderer]) -> bool:
    """Return True if the renderer uses a ``_console`` object for I/O.

    Detection works by instantiating the renderer with a minimal form
    and checking whether the instance has a ``_console`` attribute.
    """
    probe = renderer_klass(form.Form(title="", description="", questions=[]))
    return hasattr(probe, "_console")


def _render_console(
    renderer: BaseRenderer,
    inputs: list[str],
    *,
    confirm: bool = False,
) -> tuple[dict[str, Any], MagicMock]:
    """Render using a mocked ``_console`` and return (answers, input_mock).

    :param renderer: The renderer instance.
    :param inputs: Simulated user input values.
    :param confirm: Whether to render with confirmation.
    :return: A tuple of (answers_dict, input_mock).
    """
    mock_console = MagicMock()
    mock_console.input.side_effect = inputs
    setattr(renderer, "_console", mock_console)  # noqa: B010
    result = renderer.render(confirm=confirm)
    return result, mock_console.input


def _render_stdlib(
    renderer: BaseRenderer,
    inputs: list[str],
    *,
    confirm: bool = False,
) -> tuple[dict[str, Any], MagicMock]:
    """Render using patched builtins and return (answers, input_mock).

    :param renderer: The renderer instance.
    :param inputs: Simulated user input values.
    :param confirm: Whether to render with confirmation.
    :return: A tuple of (answers_dict, input_mock).
    """
    with (
        patch("builtins.input", side_effect=inputs) as mock_input,
        patch("builtins.print"),
    ):
        result = renderer.render(confirm=confirm)
    return result, mock_input


def _extract_prompts(input_mock: MagicMock) -> list[str]:
    """Extract prompt strings from an input mock's call history.

    :param input_mock: The mock that replaced ``input()`` or ``_console.input()``.
    :return: A list of prompt strings.
    """
    return [str(c.args[0]) if c.args else "" for c in input_mock.call_args_list]


@pytest.fixture
def render_form(renderer_klass: type[BaseRenderer]) -> RenderForm:
    """Return a factory that renders a form with the selected renderer.

    The patching strategy adapts automatically based on ``renderer_klass``:

    - **StdlibRenderer**: patches ``builtins.input`` and ``builtins.print``.
    - **RichRenderer / CookiecutterRenderer**: mocks the ``_console`` object.

    Override the ``renderer_klass`` fixture to switch renderers.
    """
    use_console = _has_console(renderer_klass)

    def factory(
        frm: form.Form, inputs: list[str], *, confirm: bool = False
    ) -> dict[str, Any]:
        """Render a form with preset input values.

        :param frm: The form to render.
        :param inputs: Simulated user input values.
        :param confirm: When True, enable the confirmation screen.
        :return: The collected answers dict.
        """
        renderer = renderer_klass(frm)
        render_fn = _render_console if use_console else _render_stdlib
        answers, _ = render_fn(renderer, inputs, confirm=confirm)
        return answers

    return factory


@pytest.fixture
def render_form_capture_input(
    renderer_klass: type[BaseRenderer],
) -> RenderFormCaptureInput:
    """Return a factory that renders a form and captures input prompts.

    Like ``render_form``, but also returns the prompt strings passed to
    ``input()`` (or ``_console.input()``).
    """
    use_console = _has_console(renderer_klass)

    def factory(frm: form.Form, inputs: list[str]) -> tuple[dict[str, Any], list[str]]:
        """Render a form and return (answers, list_of_input_prompts).

        :param frm: The form to render.
        :param inputs: Simulated user input values.
        :return: A tuple of (answers_dict, list_of_prompt_strings).
        """
        renderer = renderer_klass(frm)
        render_fn = _render_console if use_console else _render_stdlib
        answers, mock = render_fn(renderer, inputs)
        prompts = _extract_prompts(mock)
        return answers, prompts

    return factory
