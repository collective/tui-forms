# Changelog

<!--
   You should *NOT* be adding new change log entries to this file.
   You should create a file in the news directory instead.
   For helpful instructions, please see:
   https://collective.github.io/tui-forms/how-to-guides/contribute.html
-->

<!-- towncrier release notes start -->

## 1.0.0a3 (2026-04-02)


### Bug fixes:

- Fixed go-back losing user-entered values and reverting to schema defaults. @ericof [#16](https://github.com/collective/tui-forms/issues/16)
- Fixed computed fields not being recalculated after review retry. @ericof [#17](https://github.com/collective/tui-forms/issues/17)

## 1.0.0a2 (2026-03-30)


### New features:

- String fields now support `minLength`, `maxLength`, `pattern`, `minimum`, and `maximum` JSONSchema keywords; these constraints are enforced during rendering with clear validation error messages. @ericof [#8](https://github.com/collective/tui-forms/issues/8)
- Added a summary/confirmation screen to the form wizard. Pass `confirm=True` to `render()` to display answers before finishing; the user can confirm or restart with prior answers pre-populated. @ericof [#9](https://github.com/collective/tui-forms/issues/9)
- Added back-navigation support to all renderers: typing `<` at any prompt re-asks the previous question, with a hint displayed when going back is available. @ericof [#10](https://github.com/collective/tui-forms/issues/10)


### Bug fixes:

- Fixed ``NoInputRenderer`` infinite loop: when a default value fails validation, a ``ValueError`` is now raised immediately instead of looping forever. @ericof [#1](https://github.com/collective/tui-forms/issues/1)
- Added `ValidationError` exception class so validators can surface a specific error message; `_dispatch()` now catches it and forwards the message to `_validation_error()`. `NoInputRenderer` raises `ValueError` with the message included instead of silently looping. @ericof [#2](https://github.com/collective/tui-forms/issues/2)
- ``StdlibRenderer`` and ``CookiecutterRenderer`` now display an error message when the user enters invalid input for boolean, choice, and multiple questions, instead of silently re-prompting. @ericof [#3](https://github.com/collective/tui-forms/issues/3)
- ``$ref`` resolution now raises ``ValueError`` with the full reference path when a segment is missing, instead of a bare ``KeyError``. @ericof [#5](https://github.com/collective/tui-forms/issues/5)
- Added `required: bool = False` to `BaseQuestion`; `jsonschema_to_form` now reads the schema's `required` array and sets the flag on each question. `_dispatch()` re-prompts (or raises `ValueError` in `NoInputRenderer`) when a required field is left empty. @ericof [#6](https://github.com/collective/tui-forms/issues/6)
- `_extract_condition` now collects all property conditions from `if` blocks instead of stopping at the first one; `Form.is_active` evaluates them with AND logic so a question is only shown when every condition is met. @ericof [#7](https://github.com/collective/tui-forms/issues/7)


### Documentation:

- Updated ``noinput`` renderer reference to document that a ``ValueError`` is raised when a default value fails validation. @ericof [#1](https://github.com/collective/tui-forms/issues/1)
- Updated ``stdlib`` and ``cookiecutter`` renderer references to document the invalid input format error messages. @ericof [#3](https://github.com/collective/tui-forms/issues/3)

## 1.0.0a1 (2026-03-12)


### New features:

- Added Jinja2 template rendering for `default` values.
  Any `default` field may reference previously collected answers using `{{ answer_key }}` syntax.
  Defaults are rendered just before presenting each question, so later fields can derive their initial value from earlier answers. @ericof 
- Added `Form.user_answers` property. After `render()`, `form.user_answers` returns a dict containing only the answers that were actively provided by the user (either by accepting the suggested default or by entering a new value). Hidden computed fields and `NoInputRenderer` answers are excluded. @ericof 
- Added `create_form` and `get_renderer` to the public API. `create_form` parses a JSON Schema into a `Form` instance independently of any renderer. `get_renderer` returns a renderer class by name without instantiating it. @ericof 
- Added `jsonschema_to_form` parser that converts a standard JSONSchema document into a `Form` object ready for rendering.
  Field names, types, titles, descriptions, and defaults are all read from the schema — no Python code required to define a form. @ericof 
- Added `root_key` support on `create_renderer` and `Form`.
  When set, all answers are nested under the given key in the returned dict (e.g. `{"cookiecutter": {...}}`).
  Jinja2 default templates reference answers using `{{ root_key.answer_key }}` syntax. @ericof 
- Added `src/tui_forms/schema.json`, a JSONSchema meta-schema that describes the structure of a valid tui-forms form schema.
  Pointing an IDE or editor at this file enables autocompletion and inline validation when authoring form schemas. @ericof 
- Added a pluggable renderer architecture based on Python entry points (group `tui_forms.renderers`).
  Third-party packages can register custom renderers by declaring an entry point — no changes to `tui-forms` itself are needed.
  Installed renderers are discovered at runtime via `available_renderers()` and selected by name in `create_renderer()`. @ericof 
- Added automatic progress tracking for all renderers.
  Each user-facing question is prefixed with `[current/total]` (e.g. `[3/9]`).
  The prefix format can be overridden per renderer by implementing `_format_prefix`, or suppressed entirely by returning an empty string. @ericof 
- Added built-in input validators for standard JSONSchema format values: `email`, `idn-email`, `date` (YYYY-MM-DD), `date-time` (ISO 8601), and `data-url` (path to an existing file).
  When a field carries one of these formats, the renderer automatically re-prompts on invalid input without any extra code in the schema or renderer. @ericof 
- Added conditional question support via JSONSchema `allOf` / `if` / `then` blocks.
  A question defined inside a `then` block is only shown when its `if` condition matches the current answers, following the pattern `{properties: {key: {const: value}}}`. @ericof 
- Added full `$ref` and `$defs` / `definitions` resolution.
  Schema fragments can be defined once and referenced in multiple properties, array `items`, and `allOf` / `then` blocks.
  Inline keys placed alongside `$ref` override the referenced definition. @ericof 
- Added hidden field support via the `format` keyword.
  `format: constant` returns the raw `default` value without rendering; `format: computed` evaluates `default` as a Jinja2 template against the collected answers.
  Hidden fields are resolved automatically after all user-facing questions have been answered. @ericof 
- Added support for `type: object` properties that group related questions under a common schema key.
  The object itself is never asked; its `properties` are unpacked and presented as individual questions. @ericof 
- Added support for a `validator` key in form schema properties.
  Setting `"validator": "mypackage.validators.is_valid"` on any user-facing field loads the callable at parse time and applies it as the answer validator, re-prompting on failure.
  An empty string is treated as no validator; the key is silently ignored on hidden fields (`format: constant` or `format: computed`).
  When both `format` and `validator` are present, the explicit `validator` key takes precedence. @ericof 
- Added support for four user-facing question types: free-text (`string`, `integer`, `number`), boolean yes/no, single-choice (`oneOf` / `anyOf`), and multiple-choice (`array` with `oneOf` / `anyOf` on `items`).
  The correct type is selected automatically from the schema. @ericof 
- Added the `cookiecutter` built-in renderer (requires the `rich` extra).
  Presents questions as compact single-line prompts that match the style of the Cookiecutter scaffolding tool, making it a drop-in replacement for Cookiecutter's interactive prompt. @ericof 
- Added the `rich` built-in renderer (requires the `rich` extra).
  Displays each question inside a styled rounded panel with colour, inline validation errors, and a `[current/total]` progress prefix. @ericof 
- Added the `stdlib` built-in renderer.
  Uses only Python's standard library (`print` and `input`) with no additional dependencies.
  Supports all question types with a `[current/total] Title` prefix, inline `[default]` prompt, numbered choice menus, and comma-separated multi-select. @ericof
