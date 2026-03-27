---
myst:
  html_meta:
    "description": "Reference for the noinput renderer—a non-interactive renderer that processes a form using pre-populated answers without prompting the user."
    "property=og:description": "Reference for the noinput renderer—a non-interactive renderer that processes a form using pre-populated answers without prompting the user."
    "property=og:title": "noinput renderer"
    "keywords": "tui-forms, reference, noinput, renderer, replay, pre-populated, non-interactive"
---

# `noinput` renderer

The `noinput` renderer processes a form without prompting the user.
Every question is resolved using its pre-populated answer (when provided) or the
{term}`Jinja2`-rendered schema default.
No terminal I/O is performed.

**Renderer name:** `noinput`
**Extra required:** *(none)*

```python
from tui_forms import create_renderer

renderer = create_renderer("noinput", schema)
answers = renderer.render()
```

---

## `render` method

`noinput` inherits `render(initial_answers=None)` from {doc}`base-renderer` without changes.
See {ref}`the BaseRenderer render docs <base-renderer:render>` for the full parameter reference.

### Typical use case

Re-run a form to re-evaluate {term}`Jinja2` computed defaults against a previous
set of answers, for example after loading stored answers from disk:

```python
import json
from tui_forms import create_renderer

renderer = create_renderer("noinput", schema)

# Load answers saved from a previous session.
with open("previous_answers.json") as f:
    previous = json.load(f)

# Re-process the form without prompting the user.
answers = renderer.render(initial_answers=previous)
```

---

## How each question type is resolved

### Text field

The pre-populated answer is returned as a `str`.
When no pre-populated answer exists, the schema default is rendered by {term}`Jinja2` and returned.
When neither is available, `""` is returned.

### Boolean field

The pre-populated answer is returned as a `bool`.
When no pre-populated answer exists, the schema default is used.
When neither is available, `False` is returned.

### Single-choice field

The pre-populated answer (the `const` value of the previously selected option) is returned directly.
When no pre-populated answer exists, the schema default `const` value is used.
When neither is available, `""` is returned.

### Multiple-choice field

The pre-populated answer (a list of `const` values) is returned directly.
When no pre-populated answer exists, the schema default list is used.
When neither is available, `[]` is returned.

### Hidden fields

Computed and constant hidden fields are resolved after all user-facing questions,
following the same rules as every other renderer.

---

## Validation

Validator functions attached to questions are invoked as normal.
When an answer fails validation a `ValueError` is raised immediately, because there is
no user to re-prompt and the loop would never terminate otherwise.

```python
# Raises ValueError if the default value for any question fails its validator.
answers = renderer.render(initial_answers=previous)
```

Ensure that pre-populated answers (and schema defaults) satisfy all validators before
calling `render()`, or catch the `ValueError` in your calling code.

---

## `form.user_answers` after `noinput`

`noinput` sets `_user_provided = False`, so no answers are recorded in
`form._user_answers` during a `noinput` pass.
After `render()`, `form.user_answers` is always an empty dict.

This means you can safely use `noinput` to re-evaluate computed defaults
without polluting the `user_answers` set from a previous interactive session.
