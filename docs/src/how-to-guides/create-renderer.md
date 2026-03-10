---
myst:
  html_meta:
    "description": "Step-by-step guide to implementing a custom renderer backend for TUI Forms by subclassing BaseRenderer."
    "property=og:description": "Step-by-step guide to implementing a custom renderer backend for TUI Forms by subclassing BaseRenderer."
    "property=og:title": "Create a custom renderer"
    "keywords": "tui-forms, how-to, custom renderer, BaseRenderer, entry points, terminal, backend"
---

# Create a custom renderer

This guide walks you through implementing a custom renderer backend for TUI Forms.
A renderer is responsible for all terminal I/O: printing prompts and reading user input.
Everything else — question ordering, condition evaluation, default rendering, and hidden field resolution — is handled by {term}`BaseRenderer` automatically.

## Prerequisites

- `tui-forms` installed in your project (see {doc}`use-in-project`)
- Familiarity with Python classes and abstract methods

## Understand what you need to implement

`BaseRenderer` requires five abstract methods.
You must implement all five; the rendering pipeline calls them at the right time.

| Method | Called for |
|---|---|
| `_ask_string` | Text, integer, and number fields |
| `_ask_boolean` | Boolean (yes/no) fields |
| `_ask_choice` | Single-choice fields (`oneOf` / `anyOf`) |
| `_ask_multiple` | Multiple-choice fields (`array` + `oneOf`) |
| `_validation_error` | Any field whose validator rejects the user's input |

See {doc}`/reference/base-renderer` for the full signatures and what each method receives.

## Create the renderer class

Subclass `BaseRenderer`, set a `name` class attribute, and implement the five abstract methods.

The example below shows a minimal renderer that uses plain `print` and `input`.
Use it as a starting point and replace the I/O logic with whatever library you prefer.

```python
from tui_forms.form import BaseQuestion
from tui_forms.renderer.base import BaseRenderer
from typing import Any


class MyRenderer(BaseRenderer):
    """A minimal custom renderer using print and input."""

    name: str = "my_renderer"

    def _validation_error(self, question: BaseQuestion) -> None:
        print(f"  Invalid input for '{question.title}'. Please try again.")

    def _ask_string(self, question: BaseQuestion, default: Any, prefix: str) -> str:
        print(f"\n{prefix}{question.title}")
        if question.description:
            print(f"  {question.description}")
        default_str = str(default) if default is not None else ""
        prompt = f"  [{default_str}] " if default_str else "  "
        value = input(prompt).strip()
        return value if value else default_str

    def _ask_boolean(self, question: BaseQuestion, default: Any, prefix: str) -> bool:
        print(f"\n{prefix}{question.title}")
        if default is True:
            hint = "Y/n"
        elif default is False:
            hint = "y/N"
        else:
            hint = "y/n"
        while True:
            value = input(f"  [{hint}]: ").strip().lower()
            if not value and default is not None:
                return bool(default)
            if value in ("y", "yes"):
                return True
            if value in ("n", "no"):
                return False

    def _ask_choice(self, question: BaseQuestion, default: Any, prefix: str) -> Any:
        print(f"\n{prefix}{question.title}")
        options = question.options or []
        for i, opt in enumerate(options, 1):
            marker = ">" if opt["const"] == default else " "
            print(f"  {marker} {i}. {opt['title']}")
        while True:
            value = input("  Choice [number or enter for default]: ").strip()
            if not value and default is not None:
                return default
            if value.isdigit():
                idx = int(value) - 1
                if 0 <= idx < len(options):
                    return options[idx]["const"]

    def _ask_multiple(
        self, question: BaseQuestion, default: Any, prefix: str
    ) -> list:
        print(f"\n{prefix}{question.title}")
        options = question.options or []
        default_consts: list = default if isinstance(default, list) else []
        for i, opt in enumerate(options, 1):
            marker = "*" if opt["const"] in default_consts else " "
            print(f"  {marker} {i}. {opt['title']}")
        print("  Enter comma-separated numbers, or press enter to keep the default.")
        while True:
            value = input("  ").strip()
            if not value:
                return default_consts
            parts = [p.strip() for p in value.split(",") if p.strip()]
            if parts and all(
                p.isdigit() and 1 <= int(p) <= len(options) for p in parts
            ):
                return [options[int(p) - 1]["const"] for p in parts]
```

## Register the renderer as an entry point

TUI Forms discovers renderers through Python {term}`entry point`s in the `tui_forms.renderers` group.
Add an {term}`entry point` to your `pyproject.toml`:

```toml
[project.entry-points."tui_forms.renderers"]
my_renderer = "my_package.my_module:MyRenderer"
```

Replace `my_package.my_module` with the actual import path to the module containing your renderer class.

After editing `pyproject.toml`, reinstall the package so the {term}`entry point` is picked up:

```console
pip install -e .
```

Or, if you use `uv`:

```console
uv sync
```

## Verify the renderer is available

Use `available_renderers()` to confirm that TUI Forms can find your renderer:

```python
from tui_forms import available_renderers

print(available_renderers())
# {"stdlib": ..., "rich": ..., "my_renderer": <class MyRenderer>}
```

## Use the renderer

Pass the renderer name to `create_renderer` just like a built-in renderer:

```python
from tui_forms import create_renderer

schema = {
    "title": "Example",
    "properties": {
        "name": {"type": "string", "title": "Your name"},
    },
}

renderer = create_renderer("my_renderer", schema)
answers = renderer.render()
```

## Customise the progress prefix

By default, each question is prefixed with `[current/total]`.
Override `_format_prefix` to change the format or suppress the prefix entirely:

```python
def _format_prefix(self, current: int, total: int) -> str:
    return f"({current} of {total}) "
```

Return an empty string to suppress the prefix.
