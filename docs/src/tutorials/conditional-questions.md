---
myst:
  html_meta:
    "description": "Tutorial: show extra questions only when a previous answer matches a specific value using allOf/if/then in TUI Forms."
    "property=og:description": "Tutorial: show extra questions only when a previous answer matches a specific value using allOf/if/then in TUI Forms."
    "property=og:title": "Conditional questions"
    "keywords": "tui-forms, tutorial, conditional, allOf, if/then, dynamic form, branching"
---

# Conditional questions

In this tutorial you will build a form that shows extra questions only when a
previous answer matches a specific value.

This is useful for branching forms where some options require additional
configuration—for example, enabling a feature and then asking for its
settings.

## What you will build

A deployment configuration form that:

1. Asks which **authentication provider** to use (`none` or `oidc`).
2. Shows two extra questions—**OIDC server URL** and **client ID**—only when
   the user selects `oidc`.

## Prerequisites

- Complete {doc}`your-first-form` or be familiar with `create_renderer`.

## How conditional questions work

TUI Forms uses the standard JSONSchema `allOf` / `if` / `then` pattern.

```text
"allOf": [
  {
    "if":   { "properties": { "key": { "const": "expected_value" } } },
    "then": { "properties": { "extra_field": { <question schema> } } }
  }
]
```

When the user's answer for `key` equals `expected_value`, the questions inside
`then.properties` become active.
Otherwise they are skipped entirely—they will not appear in the returned
answers dict.

The `if` condition must follow the pattern
`{properties: {key: {const: value}}}`.
Multiple key–value pairs in a single `if` block are supported; all conditions
must match (AND logic) for the `then` questions to become active.

## Step 1—Define the base question

Start with the choice question that controls the branching:

```python
schema = {
    "title": "Deployment configuration",
    "properties": {
        "auth_provider": {
            "type": "string",
            "title": "Authentication provider",
            "default": "none",
            "oneOf": [
                {"const": "none", "title": "None"},
                {"const": "oidc", "title": "OpenID Connect (OIDC)"},
            ],
        },
    },
}
```

## Step 2—Add the conditional block

Append an `allOf` list at the top level of the schema (alongside `properties`).
Each item has an `if` condition and a `then` block with the extra questions:

```python
schema = {
    "title": "Deployment configuration",
    "properties": {
        "auth_provider": {
            "type": "string",
            "title": "Authentication provider",
            "default": "none",
            "oneOf": [
                {"const": "none", "title": "None"},
                {"const": "oidc", "title": "OpenID Connect (OIDC)"},
            ],
        },
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
                        "title": "OIDC server URL",
                        "description": "for example, https://auth.example.com/realms/myrealm",
                        "default": "",
                    },
                    "oidc_client_id": {
                        "type": "string",
                        "title": "Client ID",
                        "default": "my-app",
                    },
                }
            },
        }
    ],
}
```

## Step 3—Run the form

```python
from tui_forms import create_renderer

renderer = create_renderer("stdlib", schema)
answers = renderer.render()
print(answers)
```

## Step 4—Try both branches

Run the script and select **None** first:

```
{'auth_provider': 'none'}
```

The OIDC questions are skipped; they do not appear in the answers at all.

Run again and select **OpenID Connect (OIDC)**:

```
{'auth_provider': 'oidc', 'oidc_server_url': 'https://auth.example.com/realms/myrealm', 'oidc_client_id': 'my-app'}
```

This time both extra questions were asked and their answers are in the dict.

## Multiple conditional branches

You can add more `allOf` items to handle additional choices.
Each item is evaluated independently:

```python
"allOf": [
    {
        "if": {"properties": {"auth_provider": {"const": "oidc"}}},
        "then": {
            "properties": {
                "oidc_server_url": {"type": "string", "title": "OIDC server URL"},
                "oidc_client_id":  {"type": "string", "title": "Client ID"},
            }
        },
    },
    {
        "if": {"properties": {"auth_provider": {"const": "saml"}}},
        "then": {
            "properties": {
                "saml_metadata_url": {"type": "string", "title": "SAML metadata URL"},
            }
        },
    },
]
```

## Next steps

- {doc}`hidden-fields`: derive values automatically from what the user answered.
- {doc}`/reference/jsonschema-support`: full reference for conditional fields and `$ref` resolution.
