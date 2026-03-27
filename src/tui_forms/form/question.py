from dataclasses import dataclass
from jinja2 import Environment
from tui_forms.utils import template
from typing import Any
from typing import Protocol
from typing import TypedDict


_NOVALUE = object()


class ValidationError(Exception):
    """Raised by an AnswerValidator to report a validation failure with a message.

    Raise this instead of returning ``False`` when you want the renderer to
    display a specific error message rather than the generic retry prompt.

    Example::

        def my_validator(value: str) -> bool:
            if not value.startswith("https://"):
                raise ValidationError("URL must start with https://")
            return True
    """


class AnswerValidator(Protocol):
    """Protocol for callables that validate a question answer."""

    def __call__(self, value: str) -> bool: ...


class QuestionOption(TypedDict):
    const: Any
    title: str


class Condition(TypedDict):
    key: str
    value: Any


@dataclass
class BaseQuestion:
    """Base representation of a single form question."""

    key: str
    type: str
    title: str
    description: str
    default: Any
    options: list[QuestionOption] | None = None
    subquestions: list["BaseQuestion"] | None = None
    condition: list[Condition] | None = None
    validator: AnswerValidator | None = None
    hidden: bool = False

    def _render_variable(
        self, env: Environment, answers: dict[str, Any], value: Any, root_key: str = ""
    ) -> Any:
        key = self.key
        current_value = (answers.get(root_key, {}) if root_key else answers).get(
            key, _NOVALUE
        )
        if current_value is _NOVALUE:
            value = template.render_variable(env, value, answers)
        else:
            value = current_value
        return value

    def default_value(
        self, env: Environment, answers: dict[str, Any], root_key: str = ""
    ) -> Any:
        default_value = self._render_variable(env, answers, self.default, root_key)
        return default_value


@dataclass
class QuestionHidden(BaseQuestion):
    """A question that is not asked to the user."""

    hidden: bool = True


@dataclass
class QuestionComputed(QuestionHidden):
    """A question that is not asked and will compute the value."""

    def default_value(
        self, env: Environment, answers: dict[str, Any], root_key: str = ""
    ) -> Any:
        val = (
            self.default["default"] if isinstance(self.default, dict) else self.default
        )
        if isinstance(val, str):
            val = self._render_variable(env, answers, val, root_key)
        elif isinstance(val, list):
            val = [self._render_variable(env, answers, v, root_key) for v in val]
        elif isinstance(val, dict):
            val = {
                k: self._render_variable(env, answers, v, root_key)
                for k, v in val.items()
            }
        else:
            val = super().default_value(env, answers, root_key)
        return val


@dataclass
class QuestionConstant(QuestionHidden):
    """A question that is not asked and will always return the raw_value."""

    def default_value(
        self, env: Environment, answers: dict[str, Any], root_key: str = ""
    ) -> Any:
        """Return the raw constant value without rendering."""
        return self.default


@dataclass
class Question(BaseQuestion):
    """A question that is asked to the user."""


@dataclass
class QuestionBoolean(Question):
    """A boolean question that is asked to the user."""


@dataclass
class QuestionChoice(Question):
    """A choice question that is asked to the user."""

    def default_value(
        self, env: Environment, answers: dict[str, Any], root_key: str = ""
    ) -> Any:
        default_value = super().default_value(env, answers, root_key)
        if not isinstance(default_value, list):
            default_value = [default_value]
        return default_value[0] if default_value else ""


@dataclass
class QuestionMultiple(Question):
    """A multiple choice question that is asked to the user."""

    def default_value(
        self, env: Environment, answers: dict[str, Any], root_key: str = ""
    ) -> list:
        """Return the default as a list, coercing a scalar or None if needed.

        :param env: Jinja2 environment used to render template values.
        :param answers: Answers collected so far, used as template context.
        :param root_key: Optional root key under which answers are nested.
        :return: The default value guaranteed to be a list.
        """
        value = super().default_value(env, answers, root_key)
        if not isinstance(value, list):
            value = [value] if value is not None else []
        return value
