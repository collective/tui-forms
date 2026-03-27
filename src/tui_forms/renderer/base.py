from abc import ABC
from abc import abstractmethod
from collections.abc import Callable
from jinja2 import Environment
from tui_forms import form
from tui_forms.utils.template import create_environment
from typing import Any


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

    def render(self, initial_answers: dict[str, Any] | None = None) -> dict[str, Any]:
        """Render the form and return the collected answers.

        :param initial_answers: Optional pre-populated answers that take priority
            over schema defaults. Pass the dict exactly as returned by a previous
            ``render()`` call (root_key nesting included, when applicable).
        :return: A flat dict mapping each question key to its answer.
        """
        self._form.start()
        if initial_answers:
            self._form.answers.update(initial_answers)
        self._ask_questions(self._form.questions)
        for question in self._form.iter_all():
            if question.hidden and self._form.is_active(question):
                self._form.record(
                    question.key,
                    question.default_value(
                        self._env, self._form.answers, self._form.root_key
                    ),
                )
        return dict(self._form.answers)

    def _format_prefix(self, current: int, total: int) -> str:
        """Return the prefix string shown before each question title.

        Override this method to change the prefix format or disable it
        entirely by returning ``""``.

        :param current: 1-based index of the current question.
        :param total: Total number of user-facing questions in the form.
        :return: A prefix string such as ``"[1/9] "``.
        """
        return f"[{current}/{total}] "

    def _ask_questions(self, questions: list[form.BaseQuestion]) -> None:
        """Recursively ask all visible, non-hidden questions.

        Object-type questions with subquestions are not asked directly;
        their subquestions are asked instead.

        :param questions: The list of questions to process.
        """
        for question in questions:
            if question.hidden or not self._form.is_active(question):
                continue
            if question.type == "object" and question.subquestions:
                self._ask_questions(question.subquestions)
            else:
                self._form.advance()
                self._form.record(
                    question.key,
                    self._dispatch(question),
                    user_provided=self._user_provided,
                )

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
