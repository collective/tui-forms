---
myst:
  html_meta:
    "description": "Reference for the cookiecutter renderer—how each question type is presented in the cookiecutter prompt style using Rich."
    "property=og:description": "Reference for the cookiecutter renderer—how each question type is presented in the cookiecutter prompt style using Rich."
    "property=og:title": "cookiecutter renderer"
    "keywords": "tui-forms, reference, cookiecutter, renderer, terminal, styled, prompts"
---

# cookiecutter renderer

The `cookiecutter` renderer mimics the prompt style of the
{term}`Cookiecutter` scaffolding tool.
Text and boolean questions appear as compact single-line prompts;
choice questions show a numbered list followed by a selection prompt.
Styling uses the {term}`Rich` library.

**Renderer name:** `cookiecutter`
**Extra required:** `rich`

```console
pip install "tui-forms[rich]"
```

```python
from tui_forms import create_renderer

renderer = create_renderer("cookiecutter", schema)
answers = renderer.render()
```

---

## Text field

A text field (`type: string`, `type: integer`, `type: number`) is shown as a single
inline prompt. The progress prefix is bold cyan. The default value is shown in
parentheses (dim) immediately after the title.

```text
  [1/4] Project name (my-project):
```

*The user types a value and presses Enter, or presses Enter to accept the default.*

If no default is set, the parenthesised default is omitted:

```text
  [1/4] Project name:
```

---

## Boolean field

A boolean field (`type: boolean`) uses the same single-line prompt style.
The default is shown as `Yes` or `No` in parentheses.

Default `true`:

```text
  [2/4] Include tests? (Yes):
```

Default `false`:

```text
  [2/4] Include tests? (No):
```

*The user types `y`/`yes` or `n`/`no` and presses Enter, or presses Enter to accept the default.*

---

## Single-choice field

A single-choice field (`oneOf` or `anyOf`) prints the question title on its own line,
followed by a numbered list of options.
The selection prompt shows all valid numbers and the default index in parentheses.

```text
  [3/4] License
    1 - MIT
    2 - Apache 2.0
    3 - GNU GPL v3
    Choose from [1/2/3] (1):
```

*The user types a number and presses Enter, or presses Enter to select the default option.*

---

## Multiple-choice field

A multiple-choice field (`type: array` + `oneOf`) prints the title on its own line,
followed by a numbered list. Pre-selected options are marked with `*`; unselected options
have a leading space. The selection prompt shows the default as a comma-separated list of indices.

```text
  [4/4] Supported languages
    * 1 - English
      2 - Deutsch
      3 - Português (Brasil)
    Choose one or more from [1/2/3], comma-separated (1):
```

*The user types comma-separated numbers (for example, `1,3`) and presses Enter,
or presses Enter to keep the current selection.*

When no options are pre-selected, the default shows as `none`:

```text
    Choose one or more from [1/2/3], comma-separated (none):
```

---

## Validation error

When a field has a validator and the answer is rejected, an error is printed in red
and the same prompt is shown again:

```text
  [1/4] Project name (my-project):
  Invalid answer for 'Project name'. Please try again.
  [1/4] Project name (my-project):
```

---

```{note}
The diagrams above show plain text approximations of the terminal output.
In a real terminal, the progress prefix is coloured bold cyan and error messages
are coloured red using ANSI escape codes via the {term}`Rich` library.
```
