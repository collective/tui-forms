from tui_forms.form.question import QuestionMultiple
from tui_forms.utils.template import create_environment
from typing import Any

import pytest


@pytest.fixture
def env():
    """Return a Jinja2 environment with default settings."""
    return create_environment(None)


@pytest.fixture(scope="module")
def multiple():
    """Return a factory for QuestionMultiple instances."""

    def func(default: Any) -> QuestionMultiple:
        """Build a minimal QuestionMultiple with the given default."""
        return QuestionMultiple(
            key="x",
            type="array",
            title="X",
            description="",
            default=default,
            options=[{"const": "a", "title": "A"}, {"const": "b", "title": "B"}],
        )

    return func


@pytest.mark.parametrize(
    "default,expected,context",
    [
        (["a", "b"], ["a", "b"], {}),
        ("a", ["a"], {}),
        (None, [], {}),
        ("{{ lang }}", ["de"], {"lang": "de"}),
    ],
)
def test_default_value(env, multiple, default, expected, context):
    """QuestionMultiple.default_value always returns a list."""
    q = multiple(default)
    assert q.default_value(env, context) == expected
