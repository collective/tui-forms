from abc import ABC
from abc import abstractmethod
from collections.abc import Callable
from collections.abc import Iterator
from jinja2 import Environment
from tui_forms import form
from tui_forms.utils.template import create_environment
from typing import Any


class _GoBackRequest(Exception):
    """Raised by an _ask_* method to signal the user wants to go back."""


class BaseRenderer(ABC):
    """Abstract base for form renderers.

    Subclasses implement five abstract methods (_ask_string, _ask_boolean,
    _ask_choice, _ask_multiple, _validation_error) while this class provides
    the complete rendering flow: asking user-facing questions in order,
    respecting conditions, handling object subquestions, and finally computing
    hidden question values.
    """

    name: str = "base"
    _user_provided: bool = True
    _form: form.Form
    _env: Environment
    _BACK_COMMAND: str = "<"

    def __init__(
        self,
        frm: form.Form,
        config: dict[str, Any] | None = None,
        extensions: list[str] | None = None,
    ) -> None:
        """Initialise the renderer.

        :param frm: The form to render.
        :param config: Optional Jinja2 environment configuration.
        :param extensions: Optional list of extensions to be loaded.
        """
        self._form = frm
        self._env: Environment = create_environment(config, extensions=extensions)

    def render(
        self,
        initial_answers: dict[str, Any] | None = None,
        *,
        confirm: bool = False,
    ) -> dict[str, Any]:
        """Render the form and return the collected answers.

        When *confirm* is ``True``, :meth:`render_summary` is called after all
        questions are answered.  If the user declines to proceed, the form
        restarts with the previous answers pre-populated as defaults.

        :param initial_answers: Optional pre-populated answers that take priority
            over schema defaults. Pass the dict exactly as returned by a previous
            ``render()`` call (root_key nesting included, when applicable).
        :param confirm: When ``True``, display a summary screen after all
            questions are answered and ask the user to confirm before returning.
        :return: A flat dict mapping each question key to its answer.
        """
        current_initial = initial_answers
        while True:
            self._form.start()
            if current_initial:
                self._form.answers.update(current_initial)
            self._ask_questions(self._form.questions)
            # Remove stale answers for questions that became inactive
            # (e.g. conditional questions whose gating answer changed
            # after the user went back).
            for question in self._form.iter_all():
                if not question.hidden and not self._form.is_active(question):
                    self._form.unrecord(question.key)
            for question in self._form.iter_all():
                if question.hidden and self._form.is_active(question):
                    self._form.record(
                        question.key,
                        question.default_value(
                            self._env, self._form.answers, self._form.root_key
                        ),
                    )
            answers = dict(self._form.answers)
            if not confirm or self.render_summary(self._form.user_answers):
                return answers
            # Exclude computed (hidden) fields so they are re-evaluated
            # from scratch on the next pass using the updated answers.
            computed_keys = {q.key for q in self._form.iter_all() if q.hidden}
            current_initial = {
                k: v for k, v in answers.items() if k not in computed_keys
            }

    def render_summary(self, user_answers: dict[str, Any]) -> bool:
        """Display a summary of user-provided answers and ask for confirmation.

        Called by :meth:`render` when *confirm* is ``True``.  The default
        implementation prints a plain-text list and prompts the user to
        confirm or restart.  Override in a subclass for a richer presentation.

        :param user_answers: Answers actively provided by the user (as returned
            by ``form.user_answers``).
        :return: ``True`` to proceed with the collected answers, ``False`` to
            restart the form with the current answers pre-populated as defaults.
        """
        print("\nReview your answers:\n")
        for key, value in user_answers.items():
            question = self._question_for_key(key)
            title = question.title if question else key
            display = self._summary_display_value(question, value)
            print(f"  {title}: {display}")
        print()
        while True:
            response = input("Proceed? [Y/n]: ").strip().lower()
            if not response or response in ("y", "yes"):
                return True
            if response in ("n", "no"):
                return False
            print("  Please enter y or n.")

    def _question_for_key(self, key: str) -> form.BaseQuestion | None:
        """Return the question with the given key, or ``None`` if not found.

        :param key: The question key to look up.
        :return: The matching ``BaseQuestion``, or ``None``.
        """
        for question in self._form.iter_all():
            if question.key == key:
                return question
        return None

    def _summary_display_value(
        self, question: form.BaseQuestion | None, value: Any
    ) -> str:
        """Return a human-readable string representation of *value* for the summary.

        Booleans are shown as ``Yes`` or ``No``.  Choice and multiple-choice
        values are resolved to their option titles.  All other values are
        converted with ``str()``.

        :param question: The question the value belongs to, or ``None``.
        :param value: The answer value to format.
        :return: A display string suitable for a summary row.
        """
        if question is None:
            return str(value) if value is not None else ""
        if isinstance(question, form.QuestionBoolean):
            return "Yes" if value else "No"
        if (
            isinstance(question, (form.QuestionChoice, form.QuestionMultiple))
            and question.options
        ):
            options_map = {opt["const"]: opt["title"] for opt in question.options}
            if isinstance(value, list):
                return ", ".join(options_map.get(v, str(v)) for v in value)
            return options_map.get(value, str(value))
        return str(value) if value is not None else ""

    def _format_prefix(self, current: int, total: int) -> str:
        """Return the prefix string shown before each question title.

        Override this method to change the prefix format or disable it
        entirely by returning ``""``.

        :param current: 1-based index of the current question.
        :param total: Total number of user-facing questions in the form.
        :return: A prefix string such as ``"[1/9] "``.
        """
        return f"[{current}/{total}] "

    def _back_hint(self) -> str:
        """Return a hint string when going back is possible, or an empty string.

        :return: A hint such as ``"type < to go back"``, or ``""`` for the
            first question.
        """
        if self._form.question_index > 1:
            return f"type {self._BACK_COMMAND} to go back"
        return ""

    def _iter_active_leaves(
        self, questions: list[form.BaseQuestion]
    ) -> Iterator[form.BaseQuestion]:
        """Yield active, visible leaf questions in order.

        Object-type questions are not yielded; their subquestions are
        traversed instead.  Inactive or hidden questions are skipped.

        :param questions: The list of questions to traverse.
        """
        for question in questions:
            if question.hidden or not self._form.is_active(question):
                continue
            if question.type == "object" and question.subquestions:
                yield from self._iter_active_leaves(question.subquestions)
            else:
                yield question

    def _ask_questions(self, questions: list[form.BaseQuestion]) -> None:
        """Ask all visible, non-hidden questions with back-navigation support.

        Maintains a history stack so the user can type the back command to
        re-answer a previous question.  Active questions are recomputed on
        every iteration so conditional questions respond correctly when the
        user changes a gating answer.

        :param questions: The list of questions to process.
        """
        history: list[str] = []
        while True:
            answered = set(history)
            next_q: form.BaseQuestion | None = None
            for q in self._iter_active_leaves(questions):
                if q.key not in answered:
                    next_q = q
                    break
            if next_q is None:
                break
            self._form.set_question_index(len(history) + 1)
            try:
                answer = self._dispatch(next_q)
            except _GoBackRequest:
                if history:
                    history.pop()
                continue
            self._form.record(next_q.key, answer, user_provided=self._user_provided)
            history.append(next_q.key)

    def _dispatch(self, question: form.BaseQuestion) -> Any:
        """Dispatch to the appropriate ask method based on question type.

        Computes the prefix from the current question index before
        delegating to the concrete ask method.  Re-asks on validation
        failure, passing the validator's error message (if any) to
        ``_validation_error``.

        :param question: The question to ask.
        :return: The user's answer.
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
        while True:
            if question.required and answer in ("", [], None):
                self._validation_error(question, "This field is required.")
                answer = func(question, default, prefix)
                continue
            if question.validator is not None:
                try:
                    valid = question.validator(str(answer))
                except form.ValidationError as exc:
                    self._validation_error(question, str(exc))
                    answer = func(question, default, prefix)
                    continue
                if not valid:
                    self._validation_error(question, None)
                    answer = func(question, default, prefix)
                    continue
            break
        return answer

    @abstractmethod
    def _validation_error(
        self, question: form.BaseQuestion, message: str | None
    ) -> None:
        """Show an error message when a validator rejects the user's answer.

        :param question: The question whose answer failed validation.
        :param message: Specific error message from the validator, or ``None``
            for a generic retry prompt.
        """

    @abstractmethod
    def _ask_string(
        self, question: form.BaseQuestion, default: Any, prefix: str
    ) -> str:
        """Ask a free-text question and return the answer.

        :param question: The question to ask.
        :param default: The pre-computed default value.
        :param prefix: Progress prefix to display before the question title.
        :return: The user's answer as a string.
        """

    @abstractmethod
    def _ask_boolean(
        self, question: form.BaseQuestion, default: Any, prefix: str
    ) -> bool:
        """Ask a yes/no question and return the answer.

        :param question: The question to ask.
        :param default: The pre-computed default value.
        :param prefix: Progress prefix to display before the question title.
        :return: True or False.
        """

    @abstractmethod
    def _ask_choice(
        self, question: form.BaseQuestion, default: Any, prefix: str
    ) -> Any:
        """Ask a single-choice question and return the selected value.

        :param question: The question to ask.
        :param default: The pre-computed default value.
        :param prefix: Progress prefix to display before the question title.
        :return: The const value of the selected option.
        """

    @abstractmethod
    def _ask_multiple(
        self, question: form.BaseQuestion, default: Any, prefix: str
    ) -> list:
        """Ask a multiple-choice question and return the selected values.

        :param question: The question to ask.
        :param default: The pre-computed default value.
        :param prefix: Progress prefix to display before the question title.
        :return: A list of const values for the selected options.
        """
