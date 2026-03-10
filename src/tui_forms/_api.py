from importlib.metadata import entry_points
from tui_forms.parser import jsonschema_to_form
from tui_forms.renderer.base import BaseRenderer
from typing import Any


def available_renderers() -> dict[str, type[BaseRenderer]]:
    """Return a dict mapping renderer names to their classes."""
    renderers = entry_points(group="tui_forms.renderers")
    return {ep.name: ep.load() for ep in renderers}


def create_renderer(
    renderer: str,
    schema: dict[str, Any],
    root_key: str = "",
) -> BaseRenderer:
    """Return a renderer configured with the parsed form, ready to call render().

    :param renderer: Name of the renderer to use (e.g. ``"stdlib"``, ``"rich"``).
    :param schema: The already-loaded JSONSchema dict describing the form.
    :param root_key: Optional key to nest all answers under in the returned dict.
    :raises ValueError: If the requested renderer name is not available.
    :raises jsonschema.ValidationError: If the schema does not conform to the
        expected form structure.
    :return: A renderer instance with the parsed form attached.
    """
    renderers = available_renderers()
    if renderer not in renderers:
        available = ", ".join(sorted(renderers))
        raise ValueError(
            f"Renderer {renderer!r} not found. Available renderers: {available}"
        )
    frm = jsonschema_to_form(schema, root_key=root_key)
    return renderers[renderer](frm)
