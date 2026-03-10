from tui_forms import _api as api
from tui_forms.renderer.base import BaseRenderer

import pytest


_SIMPLE_SCHEMA: dict = {
    "title": "Test form",
    "properties": {
        "name": {"type": "string", "title": "Name", "default": "Alice"},
    },
}


@pytest.mark.parametrize("renderer_name", ["stdlib", "cookiecutter", "rich"])
def test_available_renderers(renderer_name):
    renderers = api.available_renderers()
    assert renderer_name in renderers
    klass = renderers[renderer_name]
    assert issubclass(klass, BaseRenderer)


@pytest.mark.parametrize("renderer_name", ["stdlib", "rich", "cookiecutter"])
def test_create_renderer_returns_base_renderer(renderer_name: str) -> None:
    result = api.create_renderer(renderer_name, _SIMPLE_SCHEMA)
    assert isinstance(result, BaseRenderer)


@pytest.mark.parametrize("renderer_name", ["stdlib", "rich", "cookiecutter"])
def test_create_renderer_form_has_questions(renderer_name: str) -> None:
    result = api.create_renderer(renderer_name, _SIMPLE_SCHEMA)
    assert len(result._form.questions) == 1


def test_create_renderer_root_key_applied() -> None:
    result = api.create_renderer("stdlib", _SIMPLE_SCHEMA, root_key="cookiecutter")
    assert result._form.root_key == "cookiecutter"


def test_create_renderer_unknown_renderer_raises() -> None:
    with pytest.raises(ValueError, match="Renderer 'unknown' not found"):
        api.create_renderer("unknown", _SIMPLE_SCHEMA)


def test_create_renderer_error_lists_available_renderers() -> None:
    with pytest.raises(ValueError, match="Available renderers:"):
        api.create_renderer("unknown", _SIMPLE_SCHEMA)
