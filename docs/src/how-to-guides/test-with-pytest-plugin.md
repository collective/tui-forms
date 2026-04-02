---
myst:
  html_meta:
    "description": "How to use the tui-forms pytest plugin to test your wizard implementations."
    "property=og:description": "How to use the tui-forms pytest plugin to test your wizard implementations."
    "property=og:title": "Test with the pytest plugin"
    "keywords": "tui-forms, pytest, plugin, testing, fixtures, render_form, make_form"
---

# Test with the pytest plugin

TUI Forms ships a pytest plugin that provides fixtures for testing form wizards.
Install the `test` extra and the fixtures are available automatically—no manual imports needed.

## Install the test extra

Add `tui-forms[test]` to your project's dev dependencies.

**pip**

```console
pip install "tui-forms[test]"
```

**uv**

```console
uv add --dev "tui-forms[test]"
```

## Available fixtures

The plugin registers the following fixtures.

| Fixture | Description |
|---|---|
| `make_questions` | Parse a JSONSchema dict into a list of question objects. |
| `make_form` | Build a `Form` from a JSONSchema dict (uses `make_questions` internally). |
| `render_form` | Render a form with simulated user input and return the answers dict. |
| `render_form_capture_input` | Like `render_form`, but also captures the prompt strings shown to the user. |
| `renderer_klass` | The renderer class used by `render_form`. Defaults to `StdlibRenderer`. |

## Write a basic test

Create a form from a schema and render it with simulated input.

```python
def test_project_name_is_collected(make_form, render_form):
    frm = make_form({
        "properties": {
            "name": {
                "type": "string",
                "title": "Project name",
                "default": "my-project",
            },
        }
    })
    result = render_form(frm, ["awesome-app"])
    assert result["name"] == "awesome-app"
```

## Test the confirmation screen

Pass `confirm=True` to `render_form` to exercise the summary screen.
Include the summary response (`"y"` or `"n"`) in the input list.

```python
def test_confirm_accepts_answers(make_form, render_form):
    frm = make_form({
        "properties": {
            "name": {"type": "string", "default": ""},
        }
    })
    # Answer "Alice", then confirm with "y"
    result = render_form(frm, ["Alice", "y"], confirm=True)
    assert result["name"] == "Alice"
```

## Capture input prompts

Use `render_form_capture_input` to inspect the prompt strings that were displayed.

```python
def test_default_value_shown_in_prompt(make_form, render_form_capture_input):
    frm = make_form({
        "properties": {
            "version": {
                "type": "string",
                "title": "Version",
                "default": "1.0.0",
            },
        }
    })
    result, prompts = render_form_capture_input(frm, ["2.0.0"])
    assert result["version"] == "2.0.0"
    assert "1.0.0" in prompts[0]
```

## Test with a different renderer

Override the `renderer_klass` fixture in your `conftest.py` to run the same tests against a different renderer.

```python
# conftest.py
import pytest
from tui_forms.renderer.rich import RichRenderer


@pytest.fixture
def renderer_klass():
    return RichRenderer
```

The `render_form` and `render_form_capture_input` fixtures adapt their patching strategy automatically:

- **StdlibRenderer**: patches `builtins.input` and `builtins.print`.
- **RichRenderer / CookiecutterRenderer**: mocks the internal `_console` object.

## Use with root_key

When your schema uses a `root_key` (for example, for Cookiecutter compatibility), pass it to `make_form`.

```python
def test_root_key_nesting(make_form, render_form):
    frm = make_form(
        {"properties": {"name": {"type": "string", "default": ""}}},
        root_key="cookiecutter",
    )
    result = render_form(frm, ["my-project"])
    assert result["cookiecutter"]["name"] == "my-project"
```

## Type annotations

The fixture factories conform to typed protocols exported from `tui_forms.fixtures`.
Use these for type hints in your test helpers.

```python
from tui_forms.fixtures import MakeForm, RenderForm


def my_helper(make_form: MakeForm, render_form: RenderForm) -> None:
    frm = make_form({"properties": {"x": {"type": "string", "default": ""}}})
    result = render_form(frm, ["hello"])
    assert result["x"] == "hello"
```

Available protocols:

- `MakeQuestions`
- `MakeForm`
- `RenderForm`
- `RenderFormCaptureInput`
