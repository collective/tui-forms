from jinja2 import Environment
from jinja2 import exceptions as exc
from tui_forms.utils import template
from typing import Any

import pytest


@pytest.fixture
def env() -> Environment:
    """Return a Jinja2 environment with default settings."""
    return template.create_environment({})


@pytest.mark.parametrize(
    "config",
    [
        None,
        {},
        {"jinja2_environment": []},
    ],
)
def test_create_environment(config: dict[str, Any]):
    """create_environment should return a Jinja2 Environment with the expected settings."""
    env = template.create_environment(config)
    assert env is not None
    assert isinstance(env, Environment)
    assert env.autoescape is True


@pytest.mark.parametrize(
    "raw,answers,root,expected",
    [
        ("hello", {}, "", "hello"),
        (True, {}, "", True),
        (1, {}, "", 1),
        ("{{ name }}", {"name": "Alice"}, "", "Alice"),
        (["{{ name }}"], {"name": "Alice"}, "", ["Alice"]),
        (
            ["{{ name }}", "{{ surname }}"],
            {"name": "Alice", "surname": "Smith"},
            "",
            ["Alice", "Smith"],
        ),
        ("{{ foo }}", {"name": "Alice"}, "", ""),
        ("{{ bar }}", {"name": "Alice"}, "", ""),
        ("{{ cookiecutter.name }}", {"cookiecutter": {"name": "Alice"}}, "", "Alice"),
        ("{{ cookiecutter.name }}", {"name": "Alice"}, "cookiecutter", "Alice"),
        (
            {"{{ key }}": "{{ value }}"},
            {"key": "name", "value": "Alice"},
            "",
            {"name": "Alice"},
        ),
    ],
)
def test_render_variable(
    env: Environment, raw: Any, answers: dict[str, Any], root: str, expected: Any
):
    """render_variable should render the input value as a Jinja2 template."""
    func = template.render_variable
    result = func(env, raw, answers, root)
    assert result == expected


@pytest.mark.parametrize(
    "raw,answers,root",
    [
        ("{{ cookiecutter.name }}", {"name": "Alice"}, ""),
        ("{{ foo.bar }}", {"name": "Alice"}, ""),
    ],
)
def test_render_variable_exception(
    env: Environment, raw: Any, answers: dict[str, Any], root: str
):
    """render_variable should render the input value as a Jinja2 template."""
    func = template.render_variable
    with pytest.raises(exc.UndefinedError) as exc_info:
        func(env, raw, answers, root)
    assert "is undefined" in str(exc_info.value)
