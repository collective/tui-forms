from rich.console import Console
from rich.markup import escape
from rich.text import Text
from tui_forms.form import BaseQuestion
from tui_forms.renderer.base import _GoBackRequest
from tui_forms.renderer.base import BaseRenderer
from typing import Any


class CookiecutterRenderer(BaseRenderer):
    """Form renderer that mimics the cookiecutter prompt style using rich."""

    name: str = "cookiecutter"

    def __init__(
        self,
        form: Any,
        config: dict[str, Any] | None = None,
        extensions: list[str] | None = None,
    ) -> None:
        """Initialise the renderer.

        :param form: The form to render.
        :param config: Optional Jinja2 environment configuration.
        :param extensions: Optional list of extensions to be loaded.
        """
        super().__init__(form, config, extensions=extensions)
        self._console = Console()

    def _build_inline_prompt(
        self, question: BaseQuestion, default_str: str, prefix: str
    ) -> Text:
        """Build a single-line prompt Text for string and boolean questions.

        :param question: The question to build a prompt for.
        :param default_str: The string representation of the default value.
        :param prefix: Progress prefix such as ``"[1/9] "``.
        :return: A styled Text object ready to pass to console.input().
        """
        t = Text()
        t.append("  ")
        t.append(prefix, style="bold cyan")
        t.append(escape(question.title))
        if default_str:
            t.append(f" ({escape(default_str)})", style="dim")
        t.append(": ")
        return t

    def _validation_error(self, question: BaseQuestion, message: str | None) -> None:
        """Print an error when the validator rejects the user's answer.

        :param question: The question whose answer failed validation.
        :param message: Specific error message, or ``None`` for a generic prompt.
        """
        if message:
            self._console.print(f"  [red]{message}[/]")
        else:
            self._console.print(
                f"  [red]Invalid answer for '{question.title}'. Please try again.[/]"
            )

    def _ask_string(self, question: BaseQuestion, default: Any, prefix: str) -> str:
        """Ask a free-text question using a cookiecutter-style inline prompt.

        :param question: The question to ask.
        :param default: The pre-computed default value.
        :param prefix: Progress prefix shown before the question title.
        :return: The user's answer, or the default if the input is empty.
        :raises _GoBackRequest: When the user enters the back command.
        """
        default_str = str(default) if default is not None else ""
        prompt = self._build_inline_prompt(question, default_str, prefix)
        if back_hint := self._back_hint():
            self._console.print(f"  [dim]({back_hint})[/]")
        value = self._console.input(prompt).strip()
        if value == self._BACK_COMMAND:
            raise _GoBackRequest()
        return value if value else default_str

    def _ask_boolean(self, question: BaseQuestion, default: Any, prefix: str) -> bool:
        """Ask a yes/no question, showing the default as 'Yes' or 'No'.

        :param question: The question to ask.
        :param default: The pre-computed default value (True, False, or None).
        :param prefix: Progress prefix shown before the question title.
        :return: True or False.
        :raises _GoBackRequest: When the user enters the back command.
        """
        resolved = bool(default) if default is not None else False
        default_str = "Yes" if resolved else "No"
        prompt = self._build_inline_prompt(question, default_str, prefix)
        if back_hint := self._back_hint():
            self._console.print(f"  [dim]({back_hint})[/]")
        while True:
            value = self._console.input(prompt).strip().lower()
            if value == self._BACK_COMMAND:
                raise _GoBackRequest()
            if not value:
                return resolved
            if value in ("y", "yes"):
                return True
            if value in ("n", "no"):
                return False
            self._console.print("  [red]Please enter y or n.[/]")

    def _ask_choice(self, question: BaseQuestion, default: Any, prefix: str) -> Any:
        """Ask a single-choice question using a numbered list.

        :param question: The question to ask.
        :param default: The pre-computed default const value.
        :param prefix: Progress prefix shown before the question title.
        :return: The const value of the selected option.
        :raises _GoBackRequest: When the user enters the back command.
        """
        options = question.options or []
        title_line = Text()
        title_line.append("  ")
        title_line.append(prefix, style="bold cyan")
        title_line.append(escape(question.title))
        self._console.print(title_line)
        for i, opt in enumerate(options, 1):
            self._console.print(f"    {i} - {opt['title']}")
        default_idx = next(
            (i for i, opt in enumerate(options, 1) if opt["const"] == default),
            1,
        )
        choices_str = "/".join(str(i) for i in range(1, len(options) + 1))
        prompt = Text()
        prompt.append(f"    Choose from [{choices_str}] ", style="dim")
        prompt.append(f"({default_idx})", style="dim")
        prompt.append(": ")
        if back_hint := self._back_hint():
            self._console.print(f"  [dim]({back_hint})[/]")
        while True:
            value = self._console.input(prompt).strip()
            if value == self._BACK_COMMAND:
                raise _GoBackRequest()
            if not value and default is not None:
                return default
            if value.isdigit():
                idx = int(value) - 1
                if 0 <= idx < len(options):
                    return options[idx]["const"]
            self._console.print(
                f"  [red]Please enter a number between 1 and {len(options)}.[/]"
            )

    def _ask_multiple(self, question: BaseQuestion, default: Any, prefix: str) -> list:
        """Ask a multiple-choice question using a numbered list.

        :param question: The question to ask.
        :param default: The pre-computed default list of const values.
        :param prefix: Progress prefix shown before the question title.
        :return: A list of const values for the selected options.
        :raises _GoBackRequest: When the user enters the back command.
        """
        options = question.options or []
        default_consts: list = default if isinstance(default, list) else []
        title_line = Text()
        title_line.append("  ")
        title_line.append(prefix, style="bold cyan")
        title_line.append(escape(question.title))
        self._console.print(title_line)
        for i, opt in enumerate(options, 1):
            marker = "*" if opt["const"] in default_consts else " "
            self._console.print(f"    {marker} {i} - {opt['title']}")
        default_indices = [
            str(i) for i, opt in enumerate(options, 1) if opt["const"] in default_consts
        ]
        default_str = ",".join(default_indices) if default_indices else "none"
        choices_str = "/".join(str(i) for i in range(1, len(options) + 1))
        prompt = Text()
        prompt.append(
            f"    Choose one or more from [{choices_str}], comma-separated ",
            style="dim",
        )
        prompt.append(f"({default_str})", style="dim")
        prompt.append(": ")
        if back_hint := self._back_hint():
            self._console.print(f"  [dim]({back_hint})[/]")
        while True:
            value = self._console.input(prompt).strip()
            if value == self._BACK_COMMAND:
                raise _GoBackRequest()
            if not value:
                return default_consts
            parts = [p.strip() for p in value.split(",") if p.strip()]
            if parts and all(
                p.isdigit() and 1 <= int(p) <= len(options) for p in parts
            ):
                return [options[int(p) - 1]["const"] for p in parts]
            n = len(options)
            self._console.print(
                f"  [red]Please enter comma-separated numbers between 1 and {n}.[/]"
            )
