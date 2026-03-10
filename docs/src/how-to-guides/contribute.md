---
myst:
  html_meta:
    "description": "Step-by-step guide to setting up a development environment and contributing to TUI Forms."
    "property=og:description": "Step-by-step guide to setting up a development environment and contributing to TUI Forms."
    "property=og:title": "Contribute to TUI Forms"
    "keywords": "tui-forms, contribute, development, setup, testing, pull request"
---

# Contribute to TUI Forms

This guide walks you through setting up a local development environment, running quality checks, and submitting your changes.

## Prerequisites

You need the following tools installed on your machine:

- [Git](https://git-scm.com/)
- [uv](https://docs.astral.sh/uv/): the project's package and environment manager
- [make](https://www.gnu.org/software/make/): used to run all development tasks

## Set up the development environment

Clone the repository and install all dependencies into a local virtual environment:

```console
git clone https://github.com/collective/tui-forms.git
cd tui-forms
make install
```

`make install` runs `uv sync --all-extras`, which creates a `.venv` directory with all runtime and optional dependencies installed.

## Run the tests

Run the full test suite:

```console
make test
```

Run the tests with a coverage report:

```console
make test-coverage
```

All new features, bug fixes, and refactors require tests.
See the project's testing conventions in {doc}`/concepts/index`.

## Check code quality

Format the codebase:

```console
make format
```

Run the linter:

```console
make lint
```

Check type hints:

```console
make lint-mypy
```

Run format and lint together:

```console
make check
```

Fix all issues reported by the linter before submitting your changes.

## Build the documentation

Build the HTML documentation:

```console
make docs-html
```

Preview the documentation with live reload:

```console
make docs-livehtml
```

Run the Vale style checker on the documentation:

```console
make docs-vale
```

## Code standards

### Style and formatting

- Line length: 88 characters maximum (enforced by `ruff`).
- Naming: `snake_case` for functions and variables, `PascalCase` for classes, `UPPER_SNAKE_CASE` for module-level constants.
- Imports: one import per line; `from package import name` style; no wildcard imports.
  When importing more than three names from the same package, prefer `import package` and reference them as `package.Name`.
- Use f-strings for string formatting.
- `autoescape=True` is always forced in {term}`Jinja2` environments and must not be disabled.

### Functions and classes

- Every function and class must have a docstring.
- Functions must be focused and small.
- Prefer a single `return` statement per function.
  Use an intermediate variable rather than multiple early returns:

  ```python
  # preferred
  func = self._ask_string
  if isinstance(question, QuestionBoolean):
      func = self._ask_boolean
  elif isinstance(question, QuestionChoice):
      func = self._ask_choice
  return func(question, default, prefix)
  ```

- Use `dict.get("key")` rather than `dict.get("key", None)`.
- Type hints are required on all functions, including tests.

### Testing

- Framework: `pytest` via `uv run pytest`.
- Use `pytest.mark.parametrize` for groups of similar test cases rather than duplicating test functions.
- Use `pytest` fixtures instead of module-level helper variables or functions.
- Avoid class-based test organisation; prefer plain `test_` functions.
- Every new feature, bug fix, and refactoring requires tests.
  Bug fixes must include a regression test that reproduces the original failure.

### Running checks

Run all quality checks in one step before committing:

```console
make check
```

This runs `make format` followed by `make lint`.
After that, run type-checking:

```console
make lint-mypy
```

Fix all issues reported before pushing.

---

## Changelog entry

Every pull request must include a changelog entry so that changes are captured in the release notes.
TUI Forms uses [towncrier](https://towncrier.readthedocs.io/) to manage changelog fragments.

### Create a fragment file

Add a file in the `news/` directory at the repository root.
Name the file after the GitHub issue or pull request number, followed by a dot and the fragment type:

```
news/<number>.<type>
```

For example, a bug fix for issue 42 is `news/42.bugfix`.

If no GitHub issue exists for your change, prefix the filename with `+` followed by a single word that identifies the change:

```
news/+<identifier>.<type>
```

For example, `news/+email-validator.feature`. The `+` prefix tells towncrier to treat the file as an orphan fragment not linked to any issue number.

The six allowed types are:

| Type | Use for |
|---|---|
| `breaking` | Changes that are not backwards compatible |
| `feature` | New user-facing functionality |
| `bugfix` | Bug fixes |
| `documentation` | Documentation-only changes |
| `internal` | Refactoring, dependency updates, CI changes |
| `tests` | New or changed tests that do not affect runtime behaviour |

### Write the entry

The file content should be a single short paragraph in the past tense, written in plain English.
End with an attribution in the form `@github_username`.

```
Added format-based validators for email, date, date-time, and data-url fields.
Renderers now automatically re-prompt when the user's input fails validation. @your_username
```

Keep entries user-oriented: describe what changed and why it matters, not how it was implemented.

**Good:**

> Fixed a crash when a `oneOf` option list contained a `null` value. @username

**Poor:**

> Fixed #99 by adding a None check in `_extract_options`. @username

### Preview the draft changelog

To see how your entry will appear in the release notes:

```console
make changelog
```

This runs `towncrier --draft` and prints the rendered changelog to the terminal without writing any files.

---

## Submit a pull request

1. Create a branch from `main`:
   ```console
   git checkout -b my-feature
   ```
2. Make your changes, then run `make check` and `make test` to verify everything passes.
3. Commit your changes with a descriptive message.
4. Push the branch and open a pull request against `main` on GitHub.

A pull request is ready for review when `make check`, `make test`, and `make docs-html` all pass with zero errors.
