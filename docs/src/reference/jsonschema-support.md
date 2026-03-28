---
myst:
  html_meta:
    "description": "Reference for the JSONSchema constructs supported by TUI Forms and how each maps to a question type."
    "property=og:description": "Reference for the JSONSchema constructs supported by TUI Forms and how each maps to a question type."
    "property=og:title": "JSONSchema support"
    "keywords": "tui-forms, JSONSchema, reference, question types, schema, oneOf, anyOf, allOf, if/then, $ref"
---

# JSONSchema support

TUI Forms parses a subset of {term}`JSONSchema` and converts each property into a typed question.
This page documents which schema constructs are recognised and what each one produces.

## Question type mapping

The table below summarises how a property's `type` and keywords determine the resulting question class.

| Schema construct | Question class | User-facing? |
|---|---|---|
| `type: string` / `integer` / `number` | `Question` | Yes |
| `type: boolean` | `QuestionBoolean` | Yes |
| Any scalar type + `oneOf`, `anyOf`, `options`, or `enum` | `QuestionChoice` | Yes |
| `type: array` + `oneOf` or `anyOf` on `items` | `QuestionMultiple` | Yes |
| `type: object` | *(subquestions)* | No—children are asked |
| Any type + `format: constant` | `QuestionConstant` | No |
| Any type + `format: computed` | `QuestionComputed` | No |

---

## Text fields

Any property with `type: string`, `type: integer`, or `type: number` produces a free-text `Question`.
The `title` is shown as the prompt; `description` is shown as a hint below the title.
`default` is pre-filled and accepted if the user submits an empty input.

```json
{
  "properties": {
    "project_name": {
      "type": "string",
      "title": "Project name",
      "description": "The name used in pyproject.toml.",
      "default": "my-project"
    }
  }
}
```

---

## Boolean fields

`type: boolean` produces a `QuestionBoolean`.
The renderer shows a yes/no prompt.
`default: true` pre-selects *yes*; `default: false` pre-selects *no*.

```json
{
  "properties": {
    "use_tests": {
      "type": "boolean",
      "title": "Include tests?",
      "default": true
    }
  }
}
```

---

## Single-choice fields

A property with `oneOf`, `anyOf`, or `options` produces a `QuestionChoice`.

### Using `oneOf`

Each entry must have a `const` (the stored value) and a `title` (the label shown to the user).

```json
{
  "properties": {
    "license": {
      "type": "string",
      "title": "License",
      "default": "MIT",
      "oneOf": [
        {"const": "MIT", "title": "MIT"},
        {"const": "Apache-2.0", "title": "Apache 2.0"},
        {"const": "GPL-3.0", "title": "GNU GPL v3"}
      ]
    }
  }
}
```

### Using `anyOf`

Each entry must have an `enum` array and a `title`; TUI Forms creates one option per `enum` value.

### Using `options`

The `options` key accepts a list of `[value, label]` pairs.
This is a compact alternative to `oneOf` that avoids the verbosity of full JSONSchema option objects.

```json
{
  "properties": {
    "language": {
      "type": "string",
      "title": "Language",
      "default": "en",
      "options": [
        ["en", "English"],
        ["de", "Deutsch"],
        ["pt-br", "Português (Brasil)"]
      ]
    }
  }
}
```

When `oneOf` or `anyOf` is also present, they take priority and `options` is ignored.

### Using `enum`

A bare `enum` array also produces a `QuestionChoice`.
Because JSONSchema `enum` carries no separate labels, the raw values are used
as titles by default.

```json
{
  "properties": {
    "stability": {
      "type": "string",
      "title": "Stability level",
      "default": "beta",
      "enum": ["alpha", "beta", "stable"]
    }
  }
}
```

To provide human-readable labels, add the `enumNames` extension key.
`enumNames` is not part of the JSONSchema standard, but is widely supported by
form libraries including `react-jsonschema-form`.
The list must be in the same order as `enum`; if it is shorter, the remaining
entries fall back to the raw value.

```json
{
  "properties": {
    "stability": {
      "type": "string",
      "title": "Stability level",
      "default": "beta",
      "enum": ["alpha", "beta", "stable", "deprecated"],
      "enumNames": [
        "Alpha — experimental",
        "Beta — mostly stable",
        "Stable — production ready",
        "Deprecated — no longer maintained"
      ]
    }
  }
}
```

Priority order when multiple keywords are present:
`oneOf` > `anyOf` > `options` > `enum`.

---

## Multiple-choice fields

`type: array` with `oneOf` or `anyOf` on `items` produces a `QuestionMultiple`.
The user can select zero or more options.
`default` may be a list of `const` values, a single `const` value (coerced to a list), or omitted (treated as an empty selection).

```json
{
  "properties": {
    "languages": {
      "type": "array",
      "title": "Supported languages",
      "default": ["en"],
      "items": {
        "oneOf": [
          {"const": "en", "title": "English"},
          {"const": "de", "title": "Deutsch"},
          {"const": "pt-br", "title": "Português (Brasil)"}
        ]
      }
    }
  }
}
```

---

## Object fields

`type: object` groups related questions under a common key.
The object property itself is not asked; its `properties` are unpacked and asked as individual questions.
Answers are stored flat (not nested under the object key).

```json
{
  "properties": {
    "author": {
      "type": "object",
      "title": "Author",
      "properties": {
        "name": {"type": "string", "title": "Full name"},
        "email": {"type": "string", "title": "Email address"}
      }
    }
  }
}
```

---

## Conditional fields

TUI Forms supports `allOf` blocks with `if/then` pairs.
A question defined inside a `then` block is only shown—or computed—when the `if` condition matches the current answers.

Each `if` block follows the pattern `{properties: {key: {const: value}}}`.
When the user's answer for `key` equals `value`, the `then` questions become active.
Multiple key-value pairs in a single `if` block are supported; all conditions must match for the `then` questions to become active.

```json
{
  "properties": {
    "auth_provider": {
      "type": "string",
      "title": "Authentication provider",
      "oneOf": [
        {"const": "none", "title": "None"},
        {"const": "oidc", "title": "OpenID Connect"}
      ]
    }
  },
  "allOf": [
    {
      "if": {
        "properties": {"auth_provider": {"const": "oidc"}}
      },
      "then": {
        "properties": {
          "oidc_server_url": {
            "type": "string",
            "title": "OIDC server URL"
          }
        }
      }
    }
  ]
}
```

---

## Required fields

List field keys in the top-level `required` array to mark them as mandatory.
The renderer will re-prompt if the user submits an empty value (`""`, `[]`, or nothing).

```json
{
  "required": ["site_id", "admin_email"],
  "properties": {
    "site_id": {
      "type": "string",
      "title": "Site identifier"
    },
    "admin_email": {
      "type": "string",
      "format": "email",
      "title": "Admin email"
    },
    "description": {
      "type": "string",
      "title": "Description"
    }
  }
}
```

`site_id` and `admin_email` must receive a non-empty answer; `description` is optional.

---

## Constraint keywords

TUI Forms enforces the following JSONSchema constraint keywords by attaching a
built-in validator to the question.
When the user's input violates a constraint, the renderer displays a specific
error message and re-prompts.

### String constraints

| Keyword | Validates |
|---|---|
| `minLength` | Input has at least N characters. |
| `maxLength` | Input has at most N characters. |
| `pattern` | Input matches the regular expression (full match). |

```json
{
  "properties": {
    "slug": {
      "type": "string",
      "title": "Project slug",
      "minLength": 3,
      "maxLength": 40,
      "pattern": "^[a-z0-9-]+$"
    }
  }
}
```

### Numeric constraints

| Keyword | Validates |
|---|---|
| `minimum` | Numeric value is ≥ the given number. |
| `maximum` | Numeric value is ≤ the given number. |

```json
{
  "properties": {
    "port": {
      "type": "integer",
      "title": "HTTP port",
      "minimum": 1024,
      "maximum": 65535
    }
  }
}
```

### Combining constraint keywords with a custom validator

When a field has both constraint keywords and a `validator` key (or a
format-based built-in validator), the constraints are checked first.
If they pass, the explicit validator runs.
This ensures schema-level guarantees are always enforced, regardless of what
the custom validator checks.

### Constraint keywords on hidden fields

Constraint keywords (`minLength`, `maxLength`, `pattern`, `minimum`,
`maximum`) are silently ignored on hidden fields (`format: constant` and
`format: computed`).

---

## Hidden fields

Hidden fields are never shown to the user.
TUI Forms populates them automatically after all user-facing questions have been answered.
A field is hidden when its `format` is `constant` or `computed`.

### Constant fields

`format: constant` always returns the raw `default` value, without any template rendering.
Use `type: string` for scalar values and `type: array` for list values.

```json
{
  "properties": {
    "schema_version": {
      "type": "string",
      "format": "constant",
      "title": "Schema version",
      "default": "1"
    },
    "supported_locales": {
      "type": "array",
      "format": "constant",
      "title": "Supported locales",
      "default": ["en", "pt-br"]
    }
  }
}
```

### Computed fields

`format: computed` evaluates the `default` as a {term}`Jinja2` template against the answers collected so far.
It supports string, list, and dict defaults.

```json
{
  "properties": {
    "package_name": {
      "type": "string",
      "format": "computed",
      "title": "Package name",
      "default": "{{ project_name | lower | replace('-', '_') }}"
    }
  }
}
```

---

## Format validators

The `format` keyword also enables built-in validation for standard string formats.
When a question has a recognised format, TUI Forms validates the user's input and re-prompts on failure.

| `format` value | Validates |
|---|---|
| `email` | RFC 5321 email address (`user@example.com`) |
| `idn-email` | Same validator as `email` |
| `date` | ISO 8601 calendar date (`YYYY-MM-DD`) |
| `date-time` | ISO 8601 date-time string (`YYYY-MM-DDTHH:MM:SS`) |
| `data-url` | Path to an existing file on the local filesystem |

Any other `format` value is accepted without validation.

### email

```json
{
  "properties": {
    "author_email": {
      "type": "string",
      "format": "email",
      "title": "Author email"
    }
  }
}
```

The renderer re-prompts if the entered value does not match the pattern `user@domain.tld`.

### date

```json
{
  "properties": {
    "release_date": {
      "type": "string",
      "format": "date",
      "title": "Release date",
      "description": "Format: YYYY-MM-DD"
    }
  }
}
```

The renderer re-prompts if the value cannot be parsed as `YYYY-MM-DD`.

### date-time

```json
{
  "properties": {
    "scheduled_at": {
      "type": "string",
      "format": "date-time",
      "title": "Scheduled at",
      "description": "ISO 8601 date-time, for example, 2026-01-15T09:00:00"
    }
  }
}
```

The renderer re-prompts if the value cannot be parsed by Python's `datetime.fromisoformat`.

### data-url

```json
{
  "properties": {
    "logo_path": {
      "type": "string",
      "format": "data-url",
      "title": "Logo file path"
    }
  }
}
```

The renderer re-prompts if the entered path does not point to an existing file.

---

## Custom validators

Any user-facing field can specify a custom validator via the `validator` key.
The value must be a dotted Python import path pointing to a callable that accepts
a `str` and returns a `bool`.
TUI Forms resolves and loads the callable when the schema is parsed, so an
invalid path raises immediately rather than at render time.

```json
{
  "properties": {
    "github_org": {
      "type": "string",
      "title": "GitHub organisation slug",
      "validator": "mypackage.validators.is_valid_org_slug"
    }
  }
}
```

When the user's input fails the validator, the renderer calls
`_validation_error()` and re-prompts until the validator returns `True`.
To surface a specific error message, raise `tui_forms.form.ValidationError` from
the validator instead of (or instead of returning `False`); the message is forwarded to `_validation_error()`.

An **empty string** is treated as no validator (useful as a placeholder in
schema files).

When both `format` and `validator` are present, the explicit `validator` key
takes precedence and the format-based built-in validator is not applied.

`validator` is ignored on hidden fields (`format: constant` and
`format: computed`).

---

## Schema references (`$ref` and `$defs`)

TUI Forms resolves `$ref` pointers within the same schema before parsing.
Inline overrides placed alongside `$ref` take precedence over the referenced definition.

```json
{
  "$defs": {
    "language_option": {
      "oneOf": [
        {"const": "en", "title": "English"},
        {"const": "de", "title": "Deutsch"}
      ]
    }
  },
  "properties": {
    "default_language": {
      "type": "string",
      "title": "Default language",
      "$ref": "#/$defs/language_option"
    }
  }
}
```

---

## Jinja2 defaults

The `default` value of any field may be a {term}`Jinja2` template string.
TUI Forms renders it against the answers collected so far before presenting it to the user.

```json
{
  "properties": {
    "project_name": {
      "type": "string",
      "title": "Project name",
      "default": "my-project"
    },
    "repo_name": {
      "type": "string",
      "title": "Repository name",
      "default": "{{ project_name | lower | replace(' ', '-') }}"
    }
  }
}
```

When the user answers `project_name` with `My Library`, the default for `repo_name` is pre-filled as `my-library`.

Use `{{ root_key.answer_key }}` when you set a `root_key` on the form.

---

## Demo schema

The `showcase` demo schema exercises every feature documented on this page.
Run it with any renderer:

```bash
formdemo stdlib showcase
formdemo rich showcase
formdemo cookiecutter showcase
```

The schema is at `src/tui_forms/demo/showcase.json` in the repository.

---

## Unsupported keywords

The table below lists JSONSchema keywords that TUI Forms knowingly ignores.
Including them in a schema is not an error—they are simply not processed.

| Keyword | Reason not supported |
|---|---|
| `additionalProperties` | TUI Forms generates output from declared `properties` only; there are no "additional" properties in the output, so this constraint is always satisfied by construction. |
| `minItems` / `maxItems` | Array length constraints on multiple-choice questions are not yet enforced. |
| `uniqueItems` | Duplicate selection is not yet prevented for multiple-choice questions. |
| `exclusiveMinimum` / `exclusiveMaximum` | Use `minimum` / `maximum` instead (TUI Forms uses inclusive bounds). |
| `multipleOf` | Not applicable to free-text TUI inputs. |
| `if` / `then` at the property level | Only top-level `allOf` blocks with `if/then` pairs are supported. |
| `not` | Negation logic is not supported. |
| `patternProperties` | Dynamic property keys are not supported. |
| `dependencies` / `dependentSchemas` | Use `allOf`/`if`/`then` for conditional questions instead. |
