---
myst:
  html_meta:
    "description": "Write your first TUI Forms interactive terminal form in under five minutes."
    "property=og:description": "Write your first TUI Forms interactive terminal form in under five minutes."
    "property=og:title": "Your first form"
    "keywords": "tui-forms, tutorial, getting started, first form, stdlib, terminal"
---

# Your first form

In this tutorial you will create a small interactive terminal form, run it, and
inspect the answers it returns.
No prior knowledge of TUI Forms is required.

By the end you will have a working Python script that asks the user three
questions and prints the collected answers.

## What you will build

A form that collects:

- a **project name** (free-text, with a default)
- whether to **include tests** (yes/no)
- a preferred **license** (single choice from a fixed list)

## Prerequisites

- Python 3.12 or later
- `tui-forms` installed:

  ```console
  pip install tui-forms
  ```

  Or, with `uv`:

  ```console
  uv add tui-forms
  ```

## Step 1—Define the schema

TUI Forms reads a standard {term}`JSONSchema` dict to decide what questions to
ask.
Create a new file called `first_form.py` and add the schema:

```python
schema = {
    "title": "New project",
    "properties": {
        "project_name": {
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

Each key under `properties` becomes one question:

| Key | Schema construct | Question type |
|---|---|---|
| `project_name` | `type: string` | Free-text input |
| `use_tests` | `type: boolean` | Yes/no prompt |
| `license` | `type: string` + `oneOf` | Single-choice menu |

## Step 2—Create a renderer and run the form

Add these lines after the schema definition:

```python
from tui_forms import create_renderer

renderer = create_renderer("stdlib", schema)
answers = renderer.render()
print(answers)
```

`create_renderer` parses the schema and returns a renderer ready to run.
`render()` starts the interactive session and returns a dict when the user has
answered all questions.

The full `first_form.py` script:

```python
from tui_forms import create_renderer

schema = {
    "title": "New project",
    "properties": {
        "project_name": {
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

renderer = create_renderer("stdlib", schema)
answers = renderer.render()
print(answers)
```

## Step 3—Run it

```console
python first_form.py
```

You will see three prompts, one per question.
Press **Enter** to accept the shown default, or type a new value.
After the last question the script prints the collected answers:

```
{'project_name': 'my-project', 'use_tests': True, 'license': 'MIT'}
```

## What just happened

1. `create_renderer("stdlib", schema)` parsed the schema and created a
   `StdlibRenderer`: a renderer that uses only Python's standard library for
   I/O.
2. `renderer.render()` iterated through the questions in schema order, asked
   each one, and recorded the answers.
3. The returned dict maps each property key to the value the user provided (or
   the default they accepted).

## Next steps

- Store the schema in a JSON file and load it with `json.loads(Path("form.json").read_text())`.
- Try the `rich` renderer for styled prompts: `create_renderer("rich", schema)` (requires `pip install "tui-forms[rich]"`).
- {doc}`conditional-questions`: show extra questions only when a previous answer matches a specific value.
- {doc}`/reference/jsonschema-support`: full reference for all supported schema constructs.
