# Agent Notes for tui-forms

## What This Is

A library that parses a JSONSchema and creates a form wizard to ask questions to users in a terminal.

## Architecture

Three-layer pipeline: **Parser → Form → Renderer**

- `tui_forms/_api` — Public API of the package. All methods here should be well-documented on their docstrings.
- `tui_forms/form` — Renderer-agnostic Form representation
   - `tui_forms/form/form.py` — Form implementation
   - `tui_forms/form/question.py` — Questions implementation
- `tui_forms/parser.py` — Functions to parse a JSONSchema and prepare a new `Form` instance
- `tui_forms/renderer` - Package handling the terminal integration
   - `tui_forms/renderer/base` - Base implementation of a renderer
   - `tui_forms/renderer/cookiecutter` - Renderer implemented with `rich` library
   - `tui_forms/renderer/rich` - Renderer implemented with `rich` library
   - `tui_forms/renderer/stdlib` - Renderer implemented only using Python's stdlib.
- `tui_forms/utils` - Package with helpers used elsewhere

## Question Type Hierarchy

```
BaseQuestion
├── Question          (free-text string input)
│   ├── QuestionBoolean
│   ├── QuestionChoice    (default_value() normalises list → scalar)
│   └── QuestionMultiple  (multi-select from options list)
└── QuestionHidden    (never shown to user; resolved after all user-facing questions)
    ├── QuestionConstant  (returns raw default unchanged — no template rendering)
    └── QuestionComputed  (renders default as Jinja2 template; handles str/list/dict;
                           unwraps {"default": value} dict wrapper if present)
```

Questions with `type == "object"` act as **containers**: never asked directly; their `subquestions` are recursed into (`BaseRenderer._ask_questions()`).

Dynamic defaults use `default_value(env, answers)`, which renders `default` fields as Jinja2 templates against collected answers (`src/tui_forms/utils/template.py`).

Conditional questions carry `Condition` TypedDict (`{"key": str, "value": Any}`). `BaseRenderer._is_active()` checks `answers.get(key) == value` — `False` skips both asking and computing.

## Flow

1. Parsing a representation of a form
   * Validate the form structure using JSONSchema (Not Implemented yet)
2. Create Form instance from valid form structure
   * Create a Form instance from the provided structure
   * A Form have one or more Questions
   * Question (`tui_forms.form.question.BaseQuestion`)
      * Represent one question from the form
      * Could be a user-facing question (`tui_forms.form.question.Question`) or hidden (`tui_forms.form.question.QuestionHidden`)
      * User-facing question
         * Will be asked to the user
         * Implemented either as `Question`, `QuestionBoolean`, `QuestionChoice`, `QuestionMultiple`
      * Hidden question
         * Will not be asked to the user
         * Either a `QuestionConstant` or a `QuestionComputed`
         * A `QuestionComputed` will compute the answer from previous answers

3. Renderer
   * Responsible for the input/output on the terminal
   * Support for different backends
      * Python libraries that will handle the terminal part
   * Receives a Form instance and do the form processing:
      * First ask all user-facing questions
         * Pass the existing answers to the default_value method of a `Question` to compute the initial value to be shown to the user.
      * Then process the `QuestionHidden`
         * For each `QuestionConstant` just return the `QuestionConstant.default`
         * For each `QuestionHidden` pass the existing answers to the default_value method of a `Question` to compute the initial value to be shown to the user.
      * Return the answers

## Parser: Conditional Subquestions

The parser handles JSONSchema `allOf/if/then` blocks to produce conditional subquestions. Example pattern from `tests/_resources/plone-distribution.json`:

```json
"allOf": [
  {
    "if": {"properties": {"provider": {"const": "keycloak"}}},
    "then": {"$ref": "#/definitions/keycloak"}
  }
]
```

`_build_subquestions()` resolves `$ref`, extracts the condition from the `if` block, and attaches it to each subquestion. Duplicate keys across multiple `then` branches are deduplicated.

## Adding a Renderer

Subclass `BaseRenderer` (`src/tui_forms/renderer/base.py`) and implement five abstract methods:
`_ask_string()`, `_ask_boolean()`, `_ask_choice()`, `_ask_multiple()`, `_validation_error()`.

- `stdlib.py` — minimal reference implementation (print/input)
- `rich.py` — styled terminal output with progress indicator
- `cookiecutter.py` — cookiecutter-style inline prompts

Override `_format_prefix(current, total)` to change or suppress the `[1/9]` progress prefix.

The constructor accepts an optional `config: dict` forwarded to `create_environment()` for Jinja2 customisation.

## Key Files

| File | Purpose |
|------|---------|
| `src/tui_forms/parser.py` | JSONSchema → Form; `_select_question_class()` maps schema types to question classes; handles `$ref`, `if/then`, and option extraction |
| `src/tui_forms/form/question.py` | All question types, `Condition` TypedDict, `QuestionOption` TypedDict, `AnswerValidator` Protocol |
| `src/tui_forms/renderer/base.py` | `BaseRenderer`: `_is_active()` (condition check), `_ask_questions()` (recursive traversal), `_dispatch()` (type-based routing) |
| `src/tui_forms/utils/template.py` | `render_variable()` for recursive Jinja2 template rendering on str/list/dict values |

## Guidelines

1. Package Management
   - ONLY use the local `.venv` virtual environment. Never try to install Python.
   - ONLY use uv, NEVER pip
   - Installation: `uv add package`
   - Sync: `make sync` (i.e. `uv sync --all-extras`)
   - Running tools: `uv run tool`
   - Upgrading: `uv add --dev package --upgrade-package package`
   - FORBIDDEN: `uv pip install`
   - Requires Python 3.13+

2. Code Quality
   - Type hints required for all code, including tests
   - Functions must always have docstrings
   - Functions must be focused and small
   - Follow existing patterns exactly
   - Line length: 88 chars maximum
   - Developer commands:
      - `make sync` — install/sync deps (use this, never pip)
      - `make format` — ruff format + import sort (run after every change)
      - `make lint` — ruff check --fix (run after every change)
      - `make lint-mypy` — mypy type checks (run after every change)
      - `make test-coverage` — run tests with coverage report
      - `uv run pytest` — run tests
      - `uv run formdemo stdlib|rich|cookiecutter` — interactive demo

3. Testing Requirements
   - Framework: `uv run pytest`
   - Coverage: test edge cases and errors
   - New features require tests
   - Refactoring require tests
   - Bug fixes require regression tests
   - Avoid using class-based tests if possible.
   - Use pytest.mark.parametrize for similar tests:
      - Bad:
         ```python
         def test_list_default_returned_unchanged():
            q = _multiple(["a", "b"])
            assert q.default_value(_ENV, {}) == ["a", "b"]

         def test_scalar_default_coerced_to_list():
            q = _multiple("a")
            assert q.default_value(_ENV, {}) == ["a"]

         def test_none_default_returns_empty_list():
            q = _multiple(None)
            assert q.default_value(_ENV, {}) == []

         def test_template_string_rendered_and_coerced():
            q = _multiple("{{ lang }}")
            assert q.default_value(_ENV, {"lang": "de"}) == ["de"]
         ```
      - Good:
         ```python
         @pytest.mark.parametrize(
            "default,expected,context",
            [
               (["a", "b"], ["a", "b"], {}),
               ("a", ["a"], {}),
               (None, [], {}),
               ("{{ lang }}", ["de"], {"lang": "de"}),
            ]
         )
         def test_default_value_variants(default, expected):
            q = _multiple(default)
            assert q.default_value(_ENV, {}) == expected

         ```
   - Use pytest fixtures:
      - Bad:
         ```python
         _ENV = create_environment(None)

         def _multiple(default) -> QuestionMultiple:
            """Build a minimal QuestionMultiple with the given default."""
            return QuestionMultiple(
               key="x",
               type="array",
               title="X",
               description="",
               default=default,
               options=[{"const": "a", "title": "A"}, {"const": "b", "title": "B"}],
            )


         def test_list_default_returned_unchanged():
            q = _multiple(["a", "b"])
            assert q.default_value(_ENV, {}) == ["a", "b"]
         ```
      - Good:
         ```python
         import pytest

         @pytest.fixture
         def env():
            return create_environment(None)


         @pytest.fixture(scope="module")
         def multiple():
            """Return a """

            def func(default: Any) -> QuestionMultiple:
               return QuestionMultiple(
                  key="x",
                  type="array",
                  title="X",
                  description="",
                  default=default,
                  options=[{"const": "a", "title": "A"}, {"const": "b", "title": "B"}],
               )
            return func

         def test_list_default_returned_unchanged(env, multiple):
            q = multiple(["a", "b"])
            assert q.default_value(env, {}) == ["a", "b"]
         ```

4. Changelog
   - Every new feature or bugfix **must** include a news fragment in the `news/` directory.
   - If the work is tracked by a GitHub issue, name the file `news/<issue-number>.<type>` (e.g. `news/42.feature`).
   - If there is no issue, use an orphan fragment: `news/+<short-identifier>.<type>` (e.g. `news/+my-feature.feature`).
   - Fragment types: `breaking`, `feature`, `bugfix`, `documentation`, `internal`, `tests`.
   - Write fragments in past tense, user-oriented, ending with `@github_username`.
   - Run `make changelog` to preview the rendered draft before committing.

5. Code Style
    - PEP 8 naming (snake_case for functions/variables)
    - Class names in PascalCase
    - Constants in UPPER_SNAKE_CASE
    - Document with docstrings
    - Avoid multiple `return` in a function.
      - Bad:
         ```python
         if isinstance(question, QuestionBoolean):
               return self._ask_boolean(question, default, prefix)
         if isinstance(question, QuestionMultiple):
               return self._ask_multiple(question, default, prefix)
         if isinstance(question, QuestionChoice):
               return self._ask_choice(question, default, prefix)
         return self._ask_string(question, default, prefix)
         ```
      - Better:
         ```python
         func = self._ask_string
         if isinstance(question, QuestionBoolean):
               func = self._ask_boolean
         elif isinstance(question, QuestionMultiple):
               func = self._ask_multiple
         elif isinstance(question, QuestionChoice):
               func = self._ask_choice
         return func(question, default, prefix)
         ```
    - Avoid more than three imports from the same package.
      - Bad:
         ```python
            from tui_forms.form import BaseQuestion
            from tui_forms.form import Form
            from tui_forms.form import QuestionBoolean
            from tui_forms.form import QuestionChoice
            from tui_forms.form import QuestionMultiple

            if isinstance(question, QuestionBoolean):
         ```
      - Good:
         ```python
            from tui_forms import form


            if isinstance(question, form.QuestionBoolean)
         ```
    - Never user `foo.get("default", None)` but `foo.get("default")`
    - Use f-strings for formatting
    - Imports: one import per line (ruff `force-single-line` isort config, `from-first`, `no-sections`)
    - Run `make format` after all changes, make manual adjustments when needed
    - Run `make lint` after all changes, fix all reported issues

6. Typing
   - Run `make lint-mypy` after all changes, fix all reported issues

## Notes on Optional Dependencies

- `rich` — used by `RichRenderer` and `CookiecutterRenderer`; install via `uv sync --all-extras` (or `make sync`)
