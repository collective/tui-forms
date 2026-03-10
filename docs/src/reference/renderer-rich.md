---
myst:
  html_meta:
    "description": "Reference for the rich renderer — how each question type is presented inside a styled Rich panel in the terminal."
    "property=og:description": "Reference for the rich renderer — how each question type is presented inside a styled Rich panel in the terminal."
    "property=og:title": "rich renderer"
    "keywords": "tui-forms, reference, rich, renderer, terminal, panel, styled, prompts"
---

# rich renderer

The `rich` renderer uses the {term}`Rich` library to display
each question inside a rounded panel with styled text.
The question title is shown as the panel heading; the user types inside the open bottom of the panel.

**Renderer name:** `rich`
**Extra required:** `rich`

```console
pip install "tui-forms[rich]"
```

```python
from tui_forms import create_renderer

renderer = create_renderer("rich", schema)
answers = renderer.render()
```

---

## Text field

A text field (`type: string`, `type: integer`, `type: number`) is shown inside a panel.
The progress prefix and the question title appear as the panel heading (bold cyan).
An optional description is shown in the panel body (dim text).
The default value is shown inline after `Default:`.

```text
╭─ [1/4] Project name ────────────────────────────────────╮
│ The name used in pyproject.toml.                        │
│                                                         │
│ Default [my-project]:                                   │
│ > _                                                     │
╰─────────────────────────────────────────────────────────╯
```

*The user types inside the panel and presses Enter, or presses Enter to accept the default.*

If no description is set, the body shows only the default prompt:

```text
╭─ [1/4] Project name ────────────────────────────────────╮
│                                                         │
│ Default [my-project]:                                   │
│ > _                                                     │
╰─────────────────────────────────────────────────────────╯
```

---

## Boolean field

A boolean field (`type: boolean`) shows a `Confirm (Y/n):` or `(y/N):` prompt
inside the panel. An uppercase letter indicates the default.

Default `true`:

```text
╭─ [2/4] Include tests? ──────────────────────────────────╮
│                                                         │
│ Confirm (Y/n):                                          │
│ > _                                                     │
╰─────────────────────────────────────────────────────────╯
```

Default `false`:

```text
╭─ [2/4] Include tests? ──────────────────────────────────╮
│                                                         │
│ Confirm (y/N):                                          │
│ > _                                                     │
╰─────────────────────────────────────────────────────────╯
```

*The user types `y`/`yes` or `n`/`no` and presses Enter, or presses Enter to accept the default.*
If the input is not recognised, an inline error appears and the prompt is repeated:

```text
│  Please enter y or n.
│ > _
```

---

## Single-choice field

A single-choice field (`oneOf` or `anyOf`) lists all options inside the panel.
The default option is marked with a bold green `>` and its number is shown in cyan.
Non-default options are indented with two spaces.

```text
╭─ [3/4] License ─────────────────────────────────────────╮
│                                                         │
│ > 1. MIT                                                │
│   2. Apache 2.0                                         │
│   3. GNU GPL v3                                         │
│                                                         │
│ Choice (number, or enter for default):                  │
│ > _                                                     │
╰─────────────────────────────────────────────────────────╯
```

*The user types a number and presses Enter, or presses Enter to select the marked option.*
If an invalid number is entered, an inline error appears:

```text
│  Invalid choice. Please enter a valid number.
│ > _
```

---

## Multiple-choice field

A multiple-choice field (`type: array` + `oneOf`) lists all options inside the panel.
Pre-selected items are marked with a bold green `*` and their numbers are shown in cyan.

```text
╭─ [4/4] Supported languages ─────────────────────────────╮
│                                                         │
│ * 1. English                                            │
│   2. Deutsch                                            │
│   3. Português (Brasil)                                 │
│                                                         │
│ Selection (numbers, or enter for default):              │
│ > _                                                     │
╰─────────────────────────────────────────────────────────╯
```

*The user types comma-separated numbers (e.g. `1,3`) and presses Enter,
or presses Enter to keep the current selection.*
If the input cannot be parsed, an inline error appears:

```text
│  Please enter comma-separated numbers.
│ > _
```

---

## Validation error

When a field has a validator and the answer is rejected, an error is printed in red
above the re-displayed question panel:

```text
Invalid answer for 'Project name'. Please try again.
╭─ [1/4] Project name ────────────────────────────────────╮
│                                                         │
│ Default [my-project]:                                   │
│ > _                                                     │
╰─────────────────────────────────────────────────────────╯
```

---

```{note}
The diagrams above show plain text approximations of the terminal output.
In a real terminal, the panel border uses Unicode box-drawing characters,
and the title, option numbers, and markers are coloured using ANSI escape codes.
```
