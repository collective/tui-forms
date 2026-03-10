---
myst:
  html_meta:
    "description": "Terms and definitions used throughout the TUI Forms documentation."
    "property=og:description": "Terms and definitions used throughout the TUI Forms documentation."
    "property=og:title": "Glossary"
    "keywords": "tui-forms, documentation, glossary, term, definition"
---

(glossary-label)=

# Glossary

```{glossary}
:sorted: true

TUI Forms
tui-forms
    [TUI Forms](https://collective.github.io/tui-forms) is a Python library for building interactive, schema-driven form wizards in terminal user interfaces.
    Define your form once using {term}`JSONSchema` — validation rules, field types, defaults, and all — and TUI Forms handles the rest, rendering a guided step-by-step wizard with full user input handling.

JSON Schema
JSONSchema
    [JSON Schema](https://json-schema.org/) is a declarative language for annotating and validating JSON documents' structure, constraints, and data types.
    It helps you standardize and define expectations for JSON data.
    TUI Forms uses JSONSchema as its form definition format.

Jinja2
    [Jinja2](https://jinja.palletsprojects.com/) is a fast and expressive template engine for Python.
    TUI Forms uses Jinja2 to render `default` values at runtime, allowing defaults to reference answers that the user has already provided.

react-jsonschema-form
rjsf
    [react-jsonschema-form](https://rjsf-team.github.io/react-jsonschema-form/) is a React library that renders web forms automatically from a {term}`JSONSchema` definition.
    TUI Forms is inspired by the same schema-first philosophy, applied to terminal user interfaces instead of the web.

BaseRenderer
    `BaseRenderer` is the abstract base class that all TUI Forms renderer backends extend.
    It provides the complete rendering pipeline — question ordering, condition evaluation, and hidden-field resolution — while delegating I/O to the five abstract methods (`_ask_string`, `_ask_boolean`, `_ask_choice`, `_ask_multiple`, `_validation_error`) that each concrete renderer implements.

Diátaxis
    [Diátaxis](https://diataxis.fr/) is a documentation framework that organises content into four distinct types: tutorials, how-to guides, reference, and explanation.
    The TUI Forms documentation follows this structure.

Markedly Structured Text
MyST
    [Markedly Structured Text (MyST)](https://myst-parser.readthedocs.io/en/latest/) is an extension of CommonMark Markdown that adds support for Sphinx directives and roles.
    The TUI Forms documentation is written in MyST.

CLI
    Command-Line Interface.
    A program that accepts input and produces output entirely through text in a terminal, without a graphical interface.

TUI
    Terminal User Interface.
    An interactive application that runs inside a terminal and uses text, colour, and layout to present a richer experience than a plain {term}`CLI`.

Cookiecutter
    [Cookiecutter](https://cookiecutter.readthedocs.io/) is a Python tool for generating projects from templates.
    Templates are driven by a `cookiecutter.json` file that lists the variables a user must supply.
    TUI Forms includes a `cookiecutter` renderer that mimics the Cookiecutter prompt style,
    and the `root_key` parameter can be used to produce an output dict that matches the shape Cookiecutter expects.

entry point
    A Python packaging mechanism that lets an installed package advertise named objects to other packages without requiring a direct import dependency.
    Entry points are declared in `pyproject.toml` under `[project.entry-points."group"]` and discovered at runtime using `importlib.metadata`.
    TUI Forms uses the `tui_forms.renderers` entry-point group so that renderer backends — including third-party ones — can be discovered automatically by name.

Rich
    [Rich](https://rich.readthedocs.io/) is a Python library for rendering styled text, panels, tables, and other rich output in the terminal using ANSI escape codes.
    TUI Forms uses Rich in the `rich` and `cookiecutter` renderer backends to display coloured and formatted prompts.
    Install it with the `rich` optional extra: `pip install "tui-forms[rich]"`.
```
