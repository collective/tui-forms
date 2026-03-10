from rich import box
from rich.console import Console
from rich.console import Group
from rich.panel import Panel
from rich.text import Text
from tui_forms.form import BaseQuestion
from tui_forms.form import Form
from tui_forms.renderer.base import BaseRenderer
from typing import Any


# Panel box without a bottom border.  The bottom is printed manually after
# the user finishes typing so the input cursor appears inside the box.
_OPEN_BOTTOM = box.Box("╭─┬╮\n│ ││\n├─┼┤\n│ ││\n├─┼┤\n│ ││\n│ ││\n    \n")


class RichRenderer(BaseRenderer):
    """Form renderer using the Rich library for styled terminal I/O."""

    name: str = "rich"

    def __init__(self, form: Form, config: dict[str, Any] | None = None) -> None:
        """Initialise the renderer with a shared Rich Console.

        :param form: The form to render.
        :param config: Optional Jinja2 environment configuration.
        """
        super().__init__(form, config)
        self._console = Console()

    def _show_panel(
        self, question: BaseQuestion, *body_rows: Text, prefix: str = ""
    ) -> None:
        """Build and print an open-bottom panel, then position the cursor on
        the blank bottom border line so that the next print overwrites it.

        The panel is printed with ``end=""`` so no extra newline is added after
        the blank bottom border.  An ANSI cursor-up sequence then moves the
        cursor back one line, ready for :meth:`_input_line`.

        :param question: The question whose title and description to show.
        :param body_rows: Extra rows appended after the description.
        :param prefix: Optional progress prefix shown before the title.
        """
        title = Text()
        if prefix:
            title.append(prefix, style="dim")
        title.append(question.title, style="bold cyan")
        parts: list[Text] = []
        if question.description:
            parts.append(Text(question.description, style="dim"))
        parts.extend(body_rows)
        panel = Panel(
            Group(*parts) if parts else Text(""),
            title=title,
            title_align="left",
            box=_OPEN_BOTTOM,
        )
        self._console.print(panel, end="")
        # The blank bottom border line already ends with \n, leaving the cursor
        # on the following line.  Step back up one line to overwrite it.
        self._console.file.write("\x1b[1A\r")
        self._console.file.flush()

    def _close_panel(self) -> None:
        """Print the bottom border that closes the open panel."""
        self._console.print("╰" + "─" * (self._console.width - 2) + "╯")

    def _input_line(self, prompt: str = "> ") -> str:
        """Read user input with a left border prefix so it appears inside the box.

        :param prompt: Text shown after the border character.
        :return: The stripped user input.
        """
        return self._console.input(f"│ {prompt}").strip()

    def _error_line(self, msg: str) -> None:
        """Print an error message as a line inside the still-open panel.

        :param msg: The error message to display (Rich markup supported).
        """
        self._console.print(f"│  [red]{msg}[/]")

    def _validation_error(self, question: BaseQuestion) -> None:
        """Print an error when the validator rejects the user's answer.

        :param question: The question whose answer failed validation.
        """
        self._console.print(
            f"[red]Invalid answer for '{question.title}'. Please try again.[/]"
        )

    def _ask_string(self, question: BaseQuestion, default: Any, prefix: str) -> str:
        """Ask a free-text question with the cursor inside the panel.

        :param question: The question to ask.
        :param default: The pre-computed default value.
        :param prefix: Progress prefix shown before the question title.
        :return: The user's answer, or the default if the input is empty.
        """
        default_str = str(default) if default is not None else ""
        hint = f" [dim][{default_str}][/]" if default_str else ""
        prompt_row = Text.from_markup(f"[bold]Default[/]{hint}:")
        self._show_panel(question, Text(""), prompt_row, prefix=prefix)
        value = self._input_line()
        self._close_panel()
        return value if value else default_str

    def _ask_boolean(self, question: BaseQuestion, default: Any, prefix: str) -> bool:
        """Ask a yes/no question with the cursor inside the panel.

        :param question: The question to ask.
        :param default: The pre-computed default value (True, False, or None).
        :param prefix: Progress prefix shown before the question title.
        :return: True or False.
        """
        resolved_default = bool(default) if default is not None else False
        hint = "[dim](Y/n)[/]" if resolved_default else "[dim](y/N)[/]"
        prompt_row = Text.from_markup(f"[bold]Confirm[/] {hint}:")
        self._show_panel(question, Text(""), prompt_row, prefix=prefix)
        result = None
        while result is None:
            value = self._input_line()
            if not value:
                result = resolved_default
            elif value.lower() in ("y", "yes"):
                result = True
            elif value.lower() in ("n", "no"):
                result = False
            else:
                self._error_line("Please enter y or n.")
        self._close_panel()
        return result

    def _ask_choice(self, question: BaseQuestion, default: Any, prefix: str) -> Any:
        """Ask a single-choice question with options listed inside the panel.

        :param question: The question to ask.
        :param default: The pre-computed default const value.
        :param prefix: Progress prefix shown before the question title.
        :return: The const value of the selected option.
        """
        options = question.options or []
        rows: list[Text] = []
        if question.description:
            rows.append(Text(""))
        for i, opt in enumerate(options, 1):
            if opt["const"] == default:
                rows.append(
                    Text.from_markup(f"[bold green]>[/] [cyan]{i}[/]. {opt['title']}")
                )
            else:
                rows.append(Text.from_markup(f"  [cyan]{i}[/]. {opt['title']}"))
        choice_prompt = "[bold]Choice[/] [dim](number, or enter for default)[/]:"
        rows.append(Text(""))
        rows.append(Text.from_markup(choice_prompt))
        self._show_panel(question, *rows, prefix=prefix)
        while True:
            value = self._input_line()
            if not value and default is not None:
                self._close_panel()
                return default
            if value.isdigit():
                idx = int(value) - 1
                if 0 <= idx < len(options):
                    self._close_panel()
                    return options[idx]["const"]
            self._error_line("Invalid choice. Please enter a valid number.")

    def _ask_multiple(self, question: BaseQuestion, default: Any, prefix: str) -> list:
        """Ask a multiple-choice question with options listed inside the panel.

        :param question: The question to ask.
        :param default: The pre-computed default list of const values.
        :param prefix: Progress prefix shown before the question title.
        :return: A list of const values for the selected options.
        """
        options = question.options or []
        default_consts: list = default if isinstance(default, list) else []
        rows: list[Text] = []
        if question.description:
            rows.append(Text(""))
        for i, opt in enumerate(options, 1):
            if opt["const"] in default_consts:
                rows.append(
                    Text.from_markup(f"[bold green]*[/] [cyan]{i}[/]. {opt['title']}")
                )
            else:
                rows.append(Text.from_markup(f"  [cyan]{i}[/]. {opt['title']}"))
        selection_prompt = "[bold]Selection[/] [dim](numbers, or enter for default)[/]:"
        rows.append(Text(""))
        rows.append(Text.from_markup(selection_prompt))
        self._show_panel(question, *rows, prefix=prefix)
        while True:
            value = self._input_line()
            if not value:
                self._close_panel()
                return default_consts
            parts = [p.strip() for p in value.split(",") if p.strip()]
            if parts and all(
                p.isdigit() and 1 <= int(p) <= len(options) for p in parts
            ):
                self._close_panel()
                return [options[int(p) - 1]["const"] for p in parts]
            self._error_line("Please enter comma-separated numbers.")
