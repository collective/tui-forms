---
myst:
  html_meta:
    "description": "Tutorial: attach a custom answer validator to a TUI Forms question to enforce domain-specific rules."
    "property=og:description": "Tutorial: attach a custom answer validator to a TUI Forms question to enforce domain-specific rules."
    "property=og:title": "Validating answers with a custom validator"
    "keywords": "tui-forms, tutorial, validator, AnswerValidator, custom validation, protocol"
---

# Validating answers with a custom validator

In this tutorial you will attach a custom validator to a question so that TUI
Forms re-prompts the user until they enter an acceptable value.

TUI Forms already ships with built-in validators for `format: email`,
`format: date`, `format: date-time`, and `format: data-url`.
This tutorial shows how to enforce a rule that none of the built-in formats
cover — for example, requiring a TCP port number in the range 1024–65535.

## What you will build

A server configuration form with two questions:

1. **Host name** — free text, no special validation.
2. **Port** — integer; must be between 1024 and 65535 inclusive.

If the user types an invalid port, TUI Forms re-prompts immediately.

## Prerequisites

- Complete {doc}`your-first-form` or be familiar with `create_renderer`.
- Basic familiarity with Python's `dataclasses` module.

## How validators work

`BaseQuestion` has an optional `validator` attribute that accepts any callable
matching the {class}`AnswerValidator` protocol:

```python
class AnswerValidator(Protocol):
    def __call__(self, value: str) -> bool: ...
```

When a question has a validator, `BaseRenderer._dispatch()` calls it with the
user's raw input (always a `str`) after every answer.
If it returns `False`, `_validation_error()` is called and the question is
asked again.
This loop repeats until the validator returns `True`.

## Step 1 — Parse the schema

The `create_renderer` convenience function does not expose individual question
objects, so you need to call `jsonschema_to_form` directly to get the
{class}`Form` instance before creating the renderer.

```python
from tui_forms.parser import jsonschema_to_form

schema = {
    "title": "Server configuration",
    "properties": {
        "host": {
            "type": "string",
            "title": "Host name",
            "default": "localhost",
        },
        "port": {
            "type": "integer",
            "title": "Port",
            "description": "Must be between 1024 and 65535.",
            "default": 8080,
        },
    },
}

frm = jsonschema_to_form(schema)
```

## Step 2 — Write the validator

A validator is any callable that takes a `str` and returns a `bool`.
A plain function works perfectly:

```python
def is_valid_port(value: str) -> bool:
    """Return True if value is an integer in the range 1024–65535."""
    try:
        port = int(value)
    except ValueError:
        return False
    return 1024 <= port <= 65535
```

## Step 3 — Attach the validator to the question

Iterate over `frm.questions` to find the `port` question and set its
`validator` attribute:

```python
for question in frm.questions:
    if question.key == "port":
        question.validator = is_valid_port
        break
```

`question.validator` is a plain dataclass field, so assigning to it is safe.

## Step 4 — Create the renderer and run the form

Pass the modified `Form` directly to the renderer constructor.
The `stdlib` renderer is available at `tui_forms.renderer.stdlib`:

```python
from tui_forms.renderer.stdlib import StdlibRenderer

renderer = StdlibRenderer(frm)
answers = renderer.render()
print(answers)
```

## Complete script

```python
from tui_forms.parser import jsonschema_to_form
from tui_forms.renderer.stdlib import StdlibRenderer


def is_valid_port(value: str) -> bool:
    """Return True if value is an integer in the range 1024–65535."""
    try:
        port = int(value)
    except ValueError:
        return False
    return 1024 <= port <= 65535


schema = {
    "title": "Server configuration",
    "properties": {
        "host": {
            "type": "string",
            "title": "Host name",
            "default": "localhost",
        },
        "port": {
            "type": "integer",
            "title": "Port",
            "description": "Must be between 1024 and 65535.",
            "default": 8080,
        },
    },
}

frm = jsonschema_to_form(schema)

for question in frm.questions:
    if question.key == "port":
        question.validator = is_valid_port
        break

renderer = StdlibRenderer(frm)
answers = renderer.render()
print(answers)
```

## Try it out

Run the script and enter an invalid port, for example `80`:

```
[1/2] Host name
  [localhost]
[2/2] Port
  Must be between 1024 and 65535.
  [8080] 80
  Invalid input for 'Port'. Please try again.
[2/2] Port
  Must be between 1024 and 65535.
  [8080] 8443
{'host': 'localhost', 'port': '8443'}
```

The question is repeated until the user enters a value that satisfies
`is_valid_port`.

## Using a class or lambda

Any callable works.
A lambda is fine for short rules:

```python
question.validator = lambda v: v.isdigit() and 1024 <= int(v) <= 65535
```

A class can carry configuration:

```python
class RangeValidator:
    def __init__(self, minimum: int, maximum: int) -> None:
        self.minimum = minimum
        self.maximum = maximum

    def __call__(self, value: str) -> bool:
        try:
            return self.minimum <= int(value) <= self.maximum
        except ValueError:
            return False

question.validator = RangeValidator(1024, 65535)
```

## Declaring a validator in the schema

If the validator lives in a package that is available at parse time, you can
declare it directly in the schema using the `validator` key instead of
manipulating the `Form` object in code.
The value is the same dotted import path:

```python
schema = {
    "title": "Server configuration",
    "properties": {
        "host": {
            "type": "string",
            "title": "Host name",
            "default": "localhost",
        },
        "port": {
            "type": "integer",
            "title": "Port",
            "description": "Must be between 1024 and 65535.",
            "default": 8080,
            "validator": "mypackage.validators.is_valid_port",
        },
    },
}
```

TUI Forms resolves and loads `mypackage.validators.is_valid_port` when
`create_renderer` (or `jsonschema_to_form`) is called.
A `ValueError` is raised immediately if the path cannot be imported.

Use this approach when:

- the validator is already packaged and importable
- the schema is stored as a JSON file and loaded at runtime
- you want the validation rule co-located with the field definition

Use the programmatic approach (setting `question.validator` directly) when:

- the validator is a lambda or a locally-defined function
- you need to pass configuration to the validator at runtime

## Built-in format validators

For standard formats you do not need to write a validator at all.
Declare `format` on the schema property and TUI Forms attaches the validator
for you:

| `format` | Validates |
|---|---|
| `email` | RFC 5321 email address |
| `idn-email` | Same as `email` |
| `date` | `YYYY-MM-DD` |
| `date-time` | ISO 8601 date-time |
| `data-url` | Path to an existing file |

See {doc}`/reference/jsonschema-support` for examples of each.

## Next steps

- {doc}`/how-to-guides/create-renderer` — implement a custom renderer that shows
  richer validation error messages.
- {doc}`/reference/base-renderer` — full reference for `BaseRenderer`,
  `AnswerValidator`, and the rendering pipeline.
