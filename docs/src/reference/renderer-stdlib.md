---
myst:
  html_meta:
    "description": "Reference for the stdlib renderer—how each question type is presented in the terminal using only the Python standard library."
    "property=og:description": "Reference for the stdlib renderer—how each question type is presented in the terminal using only the Python standard library."
    "property=og:title": "stdlib renderer"
    "keywords": "tui-forms, reference, stdlib, renderer, terminal, prompts, questions"
---

# stdlib renderer

The `stdlib` renderer uses only Python's built-in `print` and `input` functions.
It has no external dependencies and works in any terminal environment.

**Renderer name:** `stdlib`
**Extra required:** *(none)*

```python
from tui_forms import create_renderer

renderer = create_renderer("stdlib", schema)
answers = renderer.render()
```

---

## Text field

A text field (`type: string`, `type: integer`, `type: number`) shows the question title,
an optional description on the next line, and an inline prompt with the default in brackets.
Pressing Enter without typing accepts the default.

```text
[1/4] Project name
  The name used in pyproject.toml.
  [my-project]
```

*The user types a value and presses Enter, or presses Enter to accept `my-project`.*

If no default is set, the prompt is a bare two-space indent:

```text
[1/4] Project name

```

---

## Boolean field

A boolean field (`type: boolean`) shows a `Y/n` or `y/N` hint based on the default.
An uppercase letter indicates the pre-selected option, accepted by pressing Enter.

Default `true`:

```text
[2/4] Include tests?
  [Y/n]:
```

Default `false`:

```text
[2/4] Include tests?
  [y/N]:
```

No default set:

```text
[2/4] Include tests?
  [y/n]:
```

*The user types `y`/`yes` or `n`/`no` and presses Enter, or presses Enter to accept the default.*

---

## Single-choice field

A single-choice field (`oneOf` or `anyOf`) lists all options with a `>` marker on the default.
The user enters the option number.

```text
[3/4] License
  > 1. MIT
    2. Apache 2.0
    3. GNU GPL v3
  Choice [number or enter for default]:
```

*The user types a number and presses Enter, or presses Enter to select the marked option.*

---

## Multiple-choice field

A multiple-choice field (`type: array` + `oneOf`) lists all options with a `*` marker on each pre-selected item.
The user enters one or more comma-separated numbers.

```text
[4/4] Supported languages
  * 1. English
    2. Deutsch
    3. Português (Brasil)
  Enter comma-separated numbers, or press enter to keep default.

```

*The user types `1,3` to select English and Portuguese, or presses Enter to keep the current selection.*

---

## Validation error

When a field has a validator and the answer is rejected, the renderer prints an error
and re-shows the same prompt:

```text
[1/4] Project name
  [my-project]
  Invalid answer for 'Project name'. Please try again.

[1/4] Project name
  [my-project]
```
