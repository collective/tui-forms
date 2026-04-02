---
myst:
  html_meta:
    "description": "Reference for the tui-forms pytest plugin fixtures and their Protocol types."
    "property=og:description": "Reference for the tui-forms pytest plugin fixtures and their Protocol types."
    "property=og:title": "Pytest fixtures"
    "keywords": "tui-forms, pytest, fixtures, reference, make_form, render_form, Protocol"
---

# Pytest fixtures

TUI Forms registers a pytest plugin via the `pytest11` entry point.
Any project with `tui-forms[test]` in its dependencies gets the fixtures listed below.

See {doc}`/how-to-guides/test-with-pytest-plugin` for usage examples.

## Fixtures

### `renderer_klass`

```python
renderer_klass() -> type[BaseRenderer]
```

Returns the renderer class used by `render_form` and `render_form_capture_input`.
Defaults to `StdlibRenderer`.
Override this fixture in your `conftest.py` to test against a different renderer.

### `make_questions`

```python
make_questions(schema: dict[str, Any]) -> list[BaseQuestion]
```

Parse a JSONSchema dict and return the resulting list of question objects.

### `make_form`

```python
make_form(schema: dict[str, Any], *, root_key: str = "") -> Form
```

Build a `Form` from a JSONSchema dict.
Uses `make_questions` internally.
Pass `root_key` to nest all answers under a single key.

### `render_form`

```python
render_form(frm: Form, inputs: list[str], *, confirm: bool = False) -> dict[str, Any]
```

Render a form with simulated user input.
The patching strategy adapts automatically based on `renderer_klass`:

- **StdlibRenderer**: patches `builtins.input` and `builtins.print`.
- **RichRenderer / CookiecutterRenderer**: mocks the `_console` object.

Set `confirm=True` to exercise the confirmation screen.

### `render_form_capture_input`

```python
render_form_capture_input(frm: Form, inputs: list[str]) -> tuple[dict[str, Any], list[str]]
```

Like `render_form`, but also captures the prompt strings passed to `input()` (or `_console.input()`).
Returns a tuple of `(answers_dict, list_of_prompt_strings)`.

## Protocols

The factory callables returned by fixtures conform to typed protocols.
Import them from `tui_forms.fixtures` for type annotations.

```python
from tui_forms.fixtures import MakeForm, MakeQuestions, RenderForm, RenderFormCaptureInput
```

| Protocol | Fixture |
|---|---|
| `MakeQuestions` | `make_questions` |
| `MakeForm` | `make_form` |
| `RenderForm` | `render_form` |
| `RenderFormCaptureInput` | `render_form_capture_input` |
