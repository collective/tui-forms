---
myst:
  html_meta:
    "description": "Tutorial: use constant and computed hidden fields in TUI Forms to embed fixed values and derive answers automatically."
    "property=og:description": "Tutorial: use constant and computed hidden fields in TUI Forms to embed fixed values and derive answers automatically."
    "property=og:title": "Computed and constant hidden fields"
    "keywords": "tui-forms, tutorial, hidden fields, computed, constant, Jinja2, derived values"
---

# Computed and constant hidden fields

In this tutorial you will add fields that are never shown to the user but appear
in the final answers dict.
TUI Forms resolves them automatically after all user-facing questions have been
answered.

Two kinds of hidden field exist:

| Kind | Schema marker | Behaviour |
|---|---|---|
| **Constant** | `format: constant` | Returns the `default` value unchanged. No rendering. |
| **Computed** | `format: computed` | Evaluates the `default` as a {term}`Jinja2` template against the collected answers. |

## What you will build

A package scaffolding form that:

1. Asks for a **project name** (free text).
2. Derives a **package name** automatically by lower-casing the project name and
   replacing spaces and hyphens with underscores (computed).
3. Embeds a fixed **schema version** string that is always `"1"` (constant).

## Prerequisites

- Complete {doc}`your-first-form` or be familiar with `create_renderer`.

## Step 1 — Add a constant field

A constant field stores a fixed value that never changes regardless of what the
user types.
Set `format` to `"constant"` and provide a `default`:

```python
schema = {
    "title": "Package scaffold",
    "properties": {
        "schema_version": {
            "type": "string",
            "format": "constant",
            "title": "Schema version",
            "default": "1",
        },
    },
}
```

`schema_version` will not be asked.
The returned dict will always contain `{"schema_version": "1"}`.

## Step 2 — Add a user-facing question

Add the question whose answer the computed field will use:

```python
schema = {
    "title": "Package scaffold",
    "properties": {
        "project_name": {
            "type": "string",
            "title": "Project name",
            "default": "My Library",
        },
        "schema_version": {
            "type": "string",
            "format": "constant",
            "title": "Schema version",
            "default": "1",
        },
    },
}
```

## Step 3 — Add a computed field

A computed field evaluates its `default` as a {term}`Jinja2` template.
The template context is the answers collected so far, so you can reference any
key that was asked before the hidden fields are resolved.

Add `package_name` after `project_name`:

```python
schema = {
    "title": "Package scaffold",
    "properties": {
        "project_name": {
            "type": "string",
            "title": "Project name",
            "default": "My Library",
        },
        "package_name": {
            "type": "string",
            "format": "computed",
            "title": "Package name",
            "default": "{{ project_name | lower | replace('-', '_') | replace(' ', '_') }}",
        },
        "schema_version": {
            "type": "string",
            "format": "constant",
            "title": "Schema version",
            "default": "1",
        },
    },
}
```

The Jinja2 template `{{ project_name | lower | replace('-', '_') | replace(' ', '_') }}`
takes the `project_name` answer and transforms it into a valid Python identifier.

## Step 4 — Run the form

```python
from tui_forms import create_renderer

renderer = create_renderer("stdlib", schema)
answers = renderer.render()
print(answers)
```

Run the script.
Only `project_name` is asked.
After the user answers, TUI Forms resolves the hidden fields and returns:

```
{'project_name': 'My Library', 'package_name': 'my_library', 'schema_version': '1'}
```

Try entering a different name, for example `"Data Pipeline"`:

```
{'project_name': 'Data Pipeline', 'package_name': 'data_pipeline', 'schema_version': '1'}
```

## Constant list values

A constant field can also hold a list by using `type: array`:

```python
"supported_locales": {
    "type": "array",
    "format": "constant",
    "title": "Supported locales",
    "default": ["en", "pt-br"],
},
```

The list is returned as-is without any rendering.

## Computed list and dict values

A computed field supports list and dict defaults in addition to strings.
Each element (or value) is rendered as a Jinja2 template independently:

```python
"author_info": {
    "type": "object",
    "format": "computed",
    "title": "Author info",
    "default": {
        "name":  "{{ author_name }}",
        "email": "{{ author_email | lower }}",
    },
},
```

## Order matters

Hidden fields are resolved **after** all user-facing questions have been
answered, so a computed field can reference any answer — regardless of where it
appears in `properties`.

## Next steps

- {doc}`conditional-questions` — combine hidden fields with conditions so that a
  computed field is only resolved when a specific branch is active.
- {doc}`/reference/jsonschema-support` — full reference for `format: constant`,
  `format: computed`, and Jinja2 defaults.
