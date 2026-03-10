<div align="center">

<img alt="TUI Forms: Schema-driven form wizards for the terminal" src="https://raw.githubusercontent.com/collective/tui-forms/main/docs/src/_static/logo.svg" width="100%" />

</div>

<div align="center">

[![PyPI](https://img.shields.io/pypi/v/tui-forms)](https://pypi.org/project/tui-forms/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/tui-forms)](https://pypi.org/project/tui-forms/)
[![PyPI - Wheel](https://img.shields.io/pypi/wheel/tui-forms)](https://pypi.org/project/tui-forms/)
[![PyPI - License](https://img.shields.io/pypi/l/tui-forms)](https://pypi.org/project/tui-forms/)
[![PyPI - Status](https://img.shields.io/pypi/status/tui-forms)](https://pypi.org/project/tui-forms/)


[![CI](https://github.com/collective/tui-forms/actions/workflows/main.yml/badge.svg)](https://github.com/collective/tui-forms/actions/workflows/main.yml)

[![GitHub contributors](https://img.shields.io/github/contributors/collective/tui-forms)](https://github.com/collective/tui-forms)
[![GitHub Repo stars](https://img.shields.io/github/stars/collective/tui-forms?style=social)](https://github.com/collective/tui-forms)

</div>

**Schema-driven form wizards for the terminal.**

TUI Forms is a Python library for building interactive, schema-driven form wizards in terminal user interfaces.
Define your form once using JSONSchema — field types, validation rules, and defaults — and `tui-forms` renders a guided, step-by-step wizard in the terminal.

Inspired by `react-jsonschema-form`, it brings the same declarative, schema-first philosophy to the terminal.
Whether you are building a CLI tool, a developer scaffold, or a TUI application, TUI Forms gives you a consistent, extensible form layer without reinventing the wheel.

Full documentation: https://collective.github.io/tui-forms

## ✨ Features

- **Schema-driven forms** — define your form once using JSONSchema; field types, defaults, and validation rules live in the schema.
- **Multiple question types** — text, boolean (yes/no), single-choice, and multiple-choice questions, plus hidden constant and computed values.
- **Conditional questions** — show or hide questions based on previous answers using JSONSchema `if/then` logic.
- **Jinja2 defaults** — reference previous answers in default values using `{{ answer_key }}` template syntax.
- **Pluggable renderer backends** — use the built-in zero-dependency `stdlib` renderer, the styled `rich` renderer, the `cookiecutter`-style renderer, or implement your own by subclassing `BaseRenderer`.
- **Progress indicator** — automatically shows `[current/total]` progress as the user works through the form.

## 🚀 Quick start

```python
from tui_forms import create_renderer

schema = {
    "title": "New project",
    "properties": {
        "name": {
            "type": "string",
            "title": "Project name",
            "default": "my-project",
        },
        "use_tests": {
            "type": "boolean",
            "title": "Include tests?",
            "default": True,
        },
        "language": {
            "type": "string",
            "title": "Primary language",
            "oneOf": [
                {"const": "python", "title": "Python"},
                {"const": "rust", "title": "Rust"},
            ],
        },
    },
}

renderer = create_renderer("stdlib", schema)
answers = renderer.render()
# {"name": "my-project", "use_tests": True, "language": "python"}
```

For more examples and integration guides, see the [full documentation](https://collective.github.io/tui-forms).

## 📦 Installation

Install `tui-forms` using your preferred package manager.

The core package has no dependencies beyond the Python standard library.
Optional extras enable additional renderer backends.

**pip**

```console
pip install tui-forms
```

With the `rich` and `cookiecutter` renderer backends:

```console
pip install "tui-forms[rich]"
```

**uv**

```console
uv add tui-forms
```

**poetry**

```console
poetry add tui-forms
```

## 🛠️ Contributing

Clone the repository and set up the development environment:

```console
git clone https://github.com/collective/tui-forms.git
cd tui-forms
make install
```

Key commands:

| Command | Description |
|---|---|
| `make test` | Run all tests |
| `make test-coverage` | Run tests with coverage report |
| `make format` | Format the codebase |
| `make lint` | Run the linter |
| `make lint-mypy` | Check type hints |
| `make docs-html` | Build the HTML documentation |
| `make docs-livehtml` | Build and serve documentation locally |

For a full contributing guide, see [Contributing to TUI Forms](https://collective.github.io/tui-forms/how-to-guides/contribute.html).

## 📄 License

TUI Forms is distributed under the [MIT License](https://opensource.org/licenses/MIT).
