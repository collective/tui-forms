"""Protocol definitions for tui-forms pytest fixture factories."""

from tui_forms.form import BaseQuestion
from tui_forms.form import Form
from typing import Any
from typing import Protocol
from typing import runtime_checkable


@runtime_checkable
class MakeQuestions(Protocol):
    """Factory that parses a JSONSchema dict into a list of questions."""

    def __call__(self, schema: dict[str, Any]) -> list[BaseQuestion]:
        """Parse a JSONSchema and return the resulting questions.

        :param schema: A JSONSchema dict with a ``properties`` key.
        :return: A list of parsed question instances.
        """
        ...


@runtime_checkable
class MakeForm(Protocol):
    """Factory that builds a Form from a JSONSchema dict."""

    def __call__(self, schema: dict[str, Any], *, root_key: str = "") -> Form:
        """Build a Form from a JSONSchema dict.

        :param schema: A JSONSchema dict with a ``properties`` key.
        :param root_key: Optional key to nest all answers under.
        :return: A configured Form instance.
        """
        ...


@runtime_checkable
class RenderForm(Protocol):
    """Factory that renders a form with simulated user input."""

    def __call__(
        self,
        frm: Form,
        inputs: list[str],
        *,
        confirm: bool = False,
    ) -> dict[str, Any]:
        """Render a form with preset input values.

        :param frm: The form to render.
        :param inputs: Simulated user input values.
        :param confirm: When True, enable the confirmation screen.
        :return: The collected answers dict.
        """
        ...


@runtime_checkable
class RenderFormCaptureInput(Protocol):
    """Factory that renders a form and captures input prompts."""

    def __call__(
        self,
        frm: Form,
        inputs: list[str],
    ) -> tuple[dict[str, Any], list[str]]:
        """Render a form and return answers with captured prompts.

        :param frm: The form to render.
        :param inputs: Simulated user input values.
        :return: A tuple of (answers_dict, list_of_prompt_strings).
        """
        ...
