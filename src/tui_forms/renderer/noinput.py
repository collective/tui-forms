from collections.abc import Callable
from tui_forms import form
from tui_forms.renderer.base import BaseRenderer
from typing import Any


class NoInputRenderer(BaseRenderer):
    """Form renderer that replays previous answers without prompting the user.

    Every abstract ask method returns the resolved ``default`` value directly,
    which is either a pre-populated answer (when ``initial_answers`` was provided)
    or the Jinja2-rendered schema default.  No terminal I/O is performed.

    Typical use-case: re-run a form wizard with the answers from a previous
    session so that hidden/computed fields are re-evaluated against those answers.
    """

    name: str = "noinput"
    _user_provided: bool = False

    def render(self, initial_answers: dict[str, Any] | None = None) -> dict[str, Any]:
        """Process the form using pre-populated answers and return the result.

        :param initial_answers: Answers from a previous render() call.
            These are seeded into the form before questions are processed,
            so they take priority over schema defaults.
        :return: A flat dict mapping each question key to its answer.
        """
        return super().render(initial_answers)

    def _dispatch(self, question: form.BaseQuestion) -> Any:
        """Dispatch to the appropriate ask method and raise on validation failure.

        Overrides the base implementation to avoid an infinite loop: since
        ``_validation_error`` is a no-op and ``_ask_*`` always returns the same
        default, the base ``while`` loop would never terminate when validation
        fails.  Instead, raise ``ValueError`` immediately so callers get a
        clear, actionable error.

        :param question: The question to process.
        :return: The resolved default value.
        :raises ValueError: If the default value fails the question's validator.
        """
        prefix = self._format_prefix(
            self._form.question_index, self._form.question_total
        )
        default = question.default_value(
            self._env, self._form.answers, self._form.root_key
        )
        func: Callable[[form.BaseQuestion, Any, str], Any] = self._ask_string
        if isinstance(question, form.QuestionBoolean):
            func = self._ask_boolean
        elif isinstance(question, form.QuestionMultiple):
            func = self._ask_multiple
        elif isinstance(question, form.QuestionChoice):
            func = self._ask_choice
        answer = func(question, default, prefix)
        if question.validator is not None and not question.validator(str(answer)):
            raise ValueError(
                f"Default value {answer!r} for '{question.key}' "
                f"fails validation in no-input mode."
            )
        return answer

    def _validation_error(self, question: form.BaseQuestion) -> None:
        """No-op: there is no user to display a validation error to.

        :param question: The question whose answer failed validation.
        """

    def _ask_string(
        self, question: form.BaseQuestion, default: Any, prefix: str
    ) -> str:
        """Return the resolved default as a string.

        :param question: The question to process.
        :param default: The resolved default value.
        :param prefix: Unused progress prefix.
        :return: The default cast to str, or ``""`` if it is None.
        """
        return str(default) if default is not None else ""

    def _ask_boolean(
        self, question: form.BaseQuestion, default: Any, prefix: str
    ) -> bool:
        """Return the resolved default as a bool.

        :param question: The question to process.
        :param default: The resolved default value.
        :param prefix: Unused progress prefix.
        :return: The default cast to bool, or ``False`` if it is None.
        """
        return bool(default) if default is not None else False

    def _ask_choice(
        self, question: form.BaseQuestion, default: Any, prefix: str
    ) -> Any:
        """Return the resolved default choice value.

        :param question: The question to process.
        :param default: The resolved default const value.
        :param prefix: Unused progress prefix.
        :return: The default const value, or ``""`` if it is None.
        """
        return default if default is not None else ""

    def _ask_multiple(
        self, question: form.BaseQuestion, default: Any, prefix: str
    ) -> list:
        """Return the resolved default as a list.

        :param question: The question to process.
        :param default: The resolved default value.
        :param prefix: Unused progress prefix.
        :return: The default if it is already a list, otherwise ``[]``.
        """
        return default if isinstance(default, list) else []
