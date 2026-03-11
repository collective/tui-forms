from importlib.metadata import entry_points
from tui_forms import form
from tui_forms.parser import jsonschema_to_form
from tui_forms.renderer.base import BaseRenderer
from typing import Any


def create_form(schema: dict[str, Any], root_key: str = "") -> form.Form:
    """Parse a JSON Schema dict and return a Form instance.

    :param schema: The already-loaded JSONSchema dict describing the form.
    :param root_key: Optional key to nest all answers under in the returned dict.
    :raises jsonschema.ValidationError: If the schema does not conform to the
        expected form structure.
    :return: A parsed Form instance ready to pass to a renderer.
    """
    return jsonschema_to_form(schema, root_key=root_key)


def available_renderers() -> dict[str, type[BaseRenderer]]:
    """Return a dict mapping renderer names to their classes."""
    renderers = entry_points(group="tui_forms.renderers")
    return {ep.name: ep.load() for ep in renderers}


def get_renderer(renderer: str) -> type[BaseRenderer]:
    """Return the class implementing the named renderer.

    :param renderer: Name of the renderer to use (e.g. ``"stdlib"``, ``"rich"``).
    :raises ValueError: If the requested renderer name is not available.
    :return: A renderer class.
    """
    renderers = available_renderers()
    if renderer not in renderers:
        available = ", ".join(sorted(renderers))
        raise ValueError(
            f"Renderer {renderer!r} not found. Available renderers: {available}"
        )
    return renderers[renderer]


def create_renderer(
    renderer: str,
    schema: dict[str, Any],
    root_key: str = "",
    jinja_config: dict[str, Any] | None = None,
    jinja_extensions: list[str] | None = None,
) -> BaseRenderer:
    """Return a renderer configured with the parsed form, ready to call render().

    :param renderer: Name of the renderer to use (e.g. ``"stdlib"``, ``"rich"``).
    :param schema: The already-loaded JSONSchema dict describing the form.
    :param root_key: Optional key to nest all answers under in the returned dict.
    :param jinja_config: Optional dict with configuration to be passed to Jinja2.
    :param jinja_extensions: Optional list with extensions that need to be loaded.
    :raises ValueError: If the requested renderer name is not available.
    :raises jsonschema.ValidationError: If the schema does not conform to the
        expected form structure.
    :return: A renderer instance with the parsed form attached.
    """
    klass = get_renderer(renderer=renderer)
    frm = jsonschema_to_form(schema, root_key=root_key)
    return klass(frm, config=jinja_config, extensions=jinja_extensions)
