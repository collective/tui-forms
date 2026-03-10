from tui_forms.form import BaseQuestion
from tui_forms.renderer.base import BaseRenderer
from typing import Any


class StdlibRenderer(BaseRenderer):
    """Form renderer using Python stdlib (print / input) for terminal I/O."""

    name: str = "stdlib"

    def _print_header(self, question: BaseQuestion, prefix: str = "") -> None:
        """Print the question title and optional description.

        :param question: The question whose header to print.
        :param prefix: Progress prefix shown before the title.
        """
        print(f"\n{prefix}{question.title}")
        if question.description:
            print(f"  {question.description}")

    def _validation_error(self, question: BaseQuestion) -> None:
        """Print an error when the validator rejects the user's answer.

        :param question: The question whose answer failed validation.
        """
        print(f"  Invalid answer for '{question.title}'. Please try again.")

    def _ask_string(self, question: BaseQuestion, default: Any, prefix: str) -> str:
        """Ask a free-text question using input().

        :param question: The question to ask.
        :param default: The pre-computed default value.
        :param prefix: Progress prefix shown before the question title.
        :return: The user's answer, or the default if the input is empty.
        """
        self._print_header(question, prefix)
        default_str = str(default) if default is not None else ""
        prompt = f"  [{default_str}] " if default_str else "  "
        value = input(prompt).strip()
        return value if value else default_str

    def _ask_boolean(self, question: BaseQuestion, default: Any, prefix: str) -> bool:
        """Ask a yes/no question using input().

        :param question: The question to ask.
        :param default: The pre-computed default value (True, False, or None).
        :param prefix: Progress prefix shown before the question title.
        :return: True or False.
        """
        self._print_header(question, prefix)
        if default is True:
            hint = "Y/n"
        elif default is False:
            hint = "y/N"
        else:
            hint = "y/n"
        while True:
            value = input(f"  [{hint}]: ").strip().lower()
            if not value and default is not None:
                return bool(default)
            if value in ("y", "yes"):
                return True
            if value in ("n", "no"):
                return False

    def _ask_choice(self, question: BaseQuestion, default: Any, prefix: str) -> Any:
        """Ask a single-choice question using input().

        Displays a numbered list of options; the user enters the option
        number or presses enter to accept the default.

        :param question: The question to ask.
        :param default: The pre-computed default const value.
        :param prefix: Progress prefix shown before the question title.
        :return: The const value of the selected option.
        """
        self._print_header(question, prefix)
        options = question.options or []
        for i, opt in enumerate(options, 1):
            marker = ">" if opt["const"] == default else " "
            print(f"  {marker} {i}. {opt['title']}")
        while True:
            value = input("  Choice [number or enter for default]: ").strip()
            if not value and default is not None:
                return default
            if value.isdigit():
                idx = int(value) - 1
                if 0 <= idx < len(options):
                    return options[idx]["const"]

    def _ask_multiple(self, question: BaseQuestion, default: Any, prefix: str) -> list:
        """Ask a multiple-choice question using input().

        Displays a numbered list of options with current selections marked;
        the user enters comma-separated numbers or presses enter to accept
        the default selection.

        :param question: The question to ask.
        :param default: The pre-computed default list of const values.
        :param prefix: Progress prefix shown before the question title.
        :return: A list of const values for the selected options.
        """
        self._print_header(question, prefix)
        options = question.options or []
        default_consts: list = default if isinstance(default, list) else []
        for i, opt in enumerate(options, 1):
            marker = "*" if opt["const"] in default_consts else " "
            print(f"  {marker} {i}. {opt['title']}")
        print("  Enter comma-separated numbers, or press enter to keep default.")
        while True:
            value = input("  ").strip()
            if not value:
                return default_consts
            parts = [p.strip() for p in value.split(",") if p.strip()]
            if parts and all(
                p.isdigit() and 1 <= int(p) <= len(options) for p in parts
            ):
                return [options[int(p) - 1]["const"] for p in parts]
