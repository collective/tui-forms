from jinja2 import Environment
from typing import Any


def create_environment(
    config: dict[str, Any] | None, extensions: list[str] | None = None
) -> Environment:
    """Create a Jinja2 Environment from an optional configuration dict.

    :param config: Optional config dict; the ``jinja2_environment`` key is
        merged into the Environment constructor kwargs if present.
    :return: A configured Jinja2 Environment.
    """
    env_kwargs: dict[str, Any] = {}
    extensions = extensions if extensions else []
    if config is not None:
        env_kwargs.update(config.get("jinja2_environment", {}))
    env_kwargs.pop("autoescape", None)
    try:
        env = Environment(autoescape=True, extensions=extensions, **env_kwargs)
    except ImportError as err:
        raise RuntimeError(f"Unable to load extension: {err}") from err
    return env


def render_variable(
    env: Environment, raw: Any, answers: dict[str, Any], root_key: str = ""
) -> Any:
    """Render the next variable to be displayed in the user prompt.

    :param env: A Jinja2 Environment object.
    :param raw: The next value to be prompted for by the user.
    :param answers: The current answers.
    :param root_key: If provided, answers are nested under this key when
        rendering the template. Useful for scoped template variables.
    :return: The rendered value.
    """
    value: Any = None
    if isinstance(raw, dict):
        value = {
            render_variable(env, k, answers): render_variable(env, v, answers)
            for k, v in raw.items()
        }
    elif isinstance(raw, (list, tuple, set)):
        value = [render_variable(env, v, answers) for v in raw]
    elif isinstance(raw, (int, float, bool)) or raw is None:
        value = raw
    else:
        raw = raw if isinstance(raw, str) else str(raw)
        template = env.from_string(raw)
        payload = {root_key: answers} if root_key else answers
        value = template.render(**payload)
    return value
