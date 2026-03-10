---
myst:
  html_meta:
    "description": "Step-by-step guide to installing TUI Forms and building an interactive terminal form in your Python project."
    "property=og:description": "Step-by-step guide to installing TUI Forms and building an interactive terminal form in your Python project."
    "property=og:title": "Use TUI Forms in your project"
    "keywords": "tui-forms, how-to, install, integration, schema, renderer, terminal, wizard"
---

# Use in your project

This guide walks you through installing TUI Forms, defining a form schema, and collecting answers from the user in a terminal.

## Prerequisites

- Python 3.12 or later
- A Python project where you want to add an interactive terminal form

## Install the package

Add `tui-forms` to your project using your preferred package manager.

**pip**

```console
pip install tui-forms
```

**uv**

```console
uv add tui-forms
```

**poetry**

```console
poetry add tui-forms
```

The core package bundles the `stdlib` renderer, which has no dependencies beyond the Python standard library.
To use the styled `rich` renderer, install the `rich` extra:

```console
pip install "tui-forms[rich]"
```

## Define a form schema

TUI Forms reads a standard {term}`JSONSchema` dict to determine what questions to ask.
Each key in `properties` becomes a question.

```python
schema = {
    "title": "New project",
    "properties": {
        "name": {
            "type": "string",
            "title": "Project name",
            "default": "my-project",
        },
        "use_tests": {
            "type": "boolean",
            "title": "Include tests?",
            "default": True,
        },
        "license": {
            "type": "string",
            "title": "License",
            "default": "MIT",
            "oneOf": [
                {"const": "MIT", "title": "MIT"},
                {"const": "Apache-2.0", "title": "Apache 2.0"},
                {"const": "GPL-3.0", "title": "GNU GPL v3"},
            ],
        },
    },
}
```

See {doc}`/reference/jsonschema-support` for the full list of supported schema constructs.

## Create a renderer and collect answers

Use {func}`tui_forms.create_renderer` to parse the schema and get a renderer ready to run.
Call {meth}`render` to start the interactive form and get back a dict of answers.

```python
from tui_forms import create_renderer

renderer = create_renderer("stdlib", schema)
answers = renderer.render()
print(answers)
# {"name": "my-project", "use_tests": True, "license": "MIT"}
```

`create_renderer` accepts:

| Parameter | Type | Description |
|---|---|---|
| `renderer` | `str` | Name of the renderer to use (for example, `"stdlib"`, `"rich"`). |
| `schema` | `dict` | The loaded {term}`JSONSchema` dict describing the form. |
| `root_key` | `str` | Optional. When set, all answers are nested under this key in the returned dict. |

## Choose a renderer

TUI Forms ships with three built-in renderers.

| Renderer name | Extra required | Description |
|---|---|---|
| `stdlib` | *(none)* | Plain text prompts using only the Python standard library. |
| `cookiecutter` | `rich` | Styled prompts following the styles of `cookiecutter`, using the {term}`Rich` library. |
| `rich` | `rich` | Styled prompts using the {term}`Rich` library. |

Pass the renderer name as a string to `create_renderer`.
If the requested renderer is not installed, a `ValueError` is raised with a list of available names.

```python
renderer = create_renderer("rich", schema)
```

To discover which renderers are available in the current environment:

```python
from tui_forms import available_renderers

print(available_renderers())
# {"stdlib": <class StdlibRenderer>, "cookiecutter": <class CookiecutterRenderer>, "rich": <class RichRenderer>}
```

## Load a schema from a file

Store your schema as a JSON file and load it at runtime.

```python
import json
from pathlib import Path
from tui_forms import create_renderer

schema = json.loads(Path("form.json").read_text())
renderer = create_renderer("stdlib", schema)
answers = renderer.render()
```

## Nest answers under a root key

Pass a `root_key` to have all answers stored under a single top-level key in the returned dict.
This is useful when integrating with tools that expect a specific output shape, such as {term}`Cookiecutter`.

```python
renderer = create_renderer("stdlib", schema, root_key="cookiecutter")
answers = renderer.render()
print(answers)
# {"cookiecutter": {"name": "my-project", "use_tests": True, "license": "MIT"}}
```

When `root_key` is set, {term}`Jinja2` default templates must reference answers as `{{ root_key.answer_key }}`.
For example, with `root_key="cookiecutter"`, a computed default would be written as
`{{ cookiecutter.project_name | lower }}`.

## Next steps

- {doc}`/reference/jsonschema-support`: full reference for supported schema constructs
- {doc}`/concepts/schema-first-design`: why TUI Forms uses a schema-first approach
