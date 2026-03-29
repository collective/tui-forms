---
myst:
  html_meta:
    "description": "API reference for BaseRenderer—the abstract base class that all TUI Forms renderer backends extend."
    "property=og:description": "API reference for BaseRenderer—the abstract base class that all TUI Forms renderer backends extend."
    "property=og:title": "BaseRenderer reference"
    "keywords": "tui-forms, reference, BaseRenderer, API, renderer, abstract, _ask_string, _ask_boolean, _ask_choice, _ask_multiple, back navigation, go back"
---

# BaseRenderer

`BaseRenderer` is the abstract base class that all TUI Forms renderer backends extend.
It lives in `tui_forms.renderer.base`.

The class provides the complete rendering pipeline—question ordering, condition evaluation, {term}`Jinja2` default rendering, and hidden-field resolution—while delegating all terminal I/O to five abstract methods that each concrete renderer must implement.

## Class definition

```python
class BaseRenderer(ABC):
    name: str = "base"
    _user_provided: bool = True
```

Set `name` to a unique string identifier on your subclass.
This value is used when the renderer is discovered via `available_renderers()`.

Set `_user_provided = False` on a subclass to prevent answers recorded by
`_ask_questions` from being added to `form._user_answers`.
Use this for non-interactive renderers where no real user input takes place.
{doc}`renderer-noinput` sets this to `False`.

## Constructor

```python
def __init__(self, frm: form.Form, config: dict[str, Any] | None = None) -> None
```

| Parameter | Type | Description |
|---|---|---|
| `frm` | `form.Form` | The parsed form to render. Produced by `jsonschema_to_form` or `create_renderer`. |
| `config` | `dict \| None` | Optional {term}`Jinja2` environment configuration. See [Jinja2 configuration](#jinja2-configuration) below. |

You do not normally call this directly—use {func}`tui_forms.create_renderer` instead.

## Public method

(base-renderer:render)=
### `render`

```python
def render(self, initial_answers: dict[str, Any] | None = None) -> dict[str, Any]
```

Run the form and return the collected answers.

| Parameter | Type | Description |
|---|---|---|
| `initial_answers` | `dict \| None` | Optional pre-populated answers that take priority over schema defaults. Pass the dict exactly as returned by a previous `render()` call (`root_key` nesting included, when applicable). When `None`, schema defaults are used for all questions. |

Calls the abstract methods in order as the user progresses through the form.
After all user-facing questions are answered, resolves hidden fields automatically.

When `initial_answers` is provided, it is seeded into `form.answers` before questions
are processed. If a question's key already has a value in `form.answers` (under
`root_key` if set) before the abstract method is called, the pipeline passes that
existing value as the `default` argument instead of evaluating the {term}`Jinja2`
template. For interactive renderers, this means the pre-populated value appears as
the suggested default when the user is prompted.

**Returns:** A flat `dict` mapping each question `key` to its answer.
When `root_key` was set on the form, all answers are nested under that key.

### Inspecting user-provided answers

After `render()` returns, `form.user_answers` contains only the answers
that were actively provided by the user—either by accepting the suggested
default or by entering a new value.
Hidden computed fields and answers recorded by non-interactive renderers
(such as {doc}`renderer-noinput`) are excluded.

```python
from tui_forms import create_form, get_renderer

frm = create_form(schema)
renderer = get_renderer("stdlib")(frm)
answers = renderer.render()

# answers includes all fields (user-provided and computed)
# frm.user_answers includes only what the user actively answered
print(frm.user_answers)
```

`form.user_answers` returns a `dict[str, Any]`.
When `root_key` was set on the form, the `root_key` nesting is resolved:
the returned dict uses plain field keys, not nested keys.

## Abstract methods

You must implement all five of the following methods in your subclass.

---

### `_ask_string`

```python
@abstractmethod
def _ask_string(
    self, question: BaseQuestion, default: Any, prefix: str
) -> str
```

Ask a free-text question.
Called for fields with `type: string`, `type: integer`, or `type: number`.

| Parameter | Type | Description |
|---|---|---|
| `question` | `BaseQuestion` | The question to ask. See [BaseQuestion attributes](#basequestion-attributes). |
| `default` | `Any` | The resolved default value: a pre-populated answer if one was already recorded for this key, otherwise the {term}`Jinja2`-rendered schema default, or `None` if no default was set. |
| `prefix` | `str` | Progress prefix (for example, `"[1/5] "`) to display before the question title. |

**Returns:** The user's answer as a `str`.

---

### `_ask_boolean`

```python
@abstractmethod
def _ask_boolean(
    self, question: BaseQuestion, default: Any, prefix: str
) -> bool
```

Ask a yes/no question.
Called for fields with `type: boolean`.

| Parameter | Type | Description |
|---|---|---|
| `question` | `BaseQuestion` | The question to ask. |
| `default` | `bool \| None` | The resolved default: a pre-populated answer if already recorded, otherwise `True`, `False`, or `None` if no default was set. |
| `prefix` | `str` | Progress prefix. |

**Returns:** `True` or `False`.

---

### `_ask_choice`

```python
@abstractmethod
def _ask_choice(
    self, question: BaseQuestion, default: Any, prefix: str
) -> Any
```

Ask a single-choice question.
Called for fields that have `oneOf` or `anyOf`.
The available options are in `question.options`.

| Parameter | Type | Description |
|---|---|---|
| `question` | `BaseQuestion` | The question to ask. `question.options` holds the list of choices. |
| `default` | `Any` | The resolved default: a pre-populated answer if already recorded, otherwise the `const` value of the schema-defined pre-selected option, or `""` if none. |
| `prefix` | `str` | Progress prefix. |

**Returns:** The `const` value of the selected option.

---

### `_ask_multiple`

```python
@abstractmethod
def _ask_multiple(
    self, question: BaseQuestion, default: Any, prefix: str
) -> list
```

Ask a multiple-choice question.
Called for fields with `type: array` and `oneOf` or `anyOf` on `items`.
The available options are in `question.options`.

| Parameter | Type | Description |
|---|---|---|
| `question` | `BaseQuestion` | The question to ask. `question.options` holds the list of choices. |
| `default` | `list` | The resolved default: a pre-populated answer if already recorded, otherwise the list of `const` values that are pre-selected from the schema. May be empty. |
| `prefix` | `str` | Progress prefix. |

**Returns:** A `list` of `const` values for the selected options.

---

### `_validation_error`

```python
@abstractmethod
def _validation_error(
    self, question: BaseQuestion, message: str | None
) -> None
```

Display an error message when the user's answer fails the field's validator or
a required field is left empty.
Called automatically by the rendering pipeline before re-prompting the question.

| Parameter | Type | Description |
|---|---|---|
| `question` | `BaseQuestion` | The question whose answer failed validation. |
| `message` | `str \| None` | The specific error message from the validator (when the validator raised `ValidationError`), or `None` for a generic "please try again" prompt. For `required` failures the pipeline passes `"This field is required."`. |

---

## Overridable methods

### `_format_prefix`

```python
def _format_prefix(self, current: int, total: int) -> str
```

Return the progress prefix prepended to each question title.
The default implementation returns `"[current/total] "` (for example, `"[3/9] "`).

Override this method to change the format or return `""` to suppress the prefix.

| Parameter | Type | Description |
|---|---|---|
| `current` | `int` | 1-based index of the current question. |
| `total` | `int` | Total number of user-facing questions. |

**Returns:** A `str` prefix, or `""` to show no prefix.

---

### `_back_hint`

```python
def _back_hint(self) -> str
```

Return a short hint string to display when going back is possible, or an empty
string when the first question is being asked (there is nothing to go back to).

The default implementation returns `"type < to go back"` when
`form.question_index > 1`, and `""` otherwise.

Override this method to change the hint text or suppress it by returning `""`.

**Returns:** A hint `str`, or `""` for the first question.

---

## Back navigation

All interactive `_ask_*` methods should support back navigation so that users
can correct a previous answer.

### How it works

The rendering pipeline (`_ask_questions`) maintains a history stack of answered
question keys.
When an `_ask_*` method raises `_GoBackRequest`, the pipeline pops the most
recent key from the history, removes the stored answer, and re-asks that question.
This means:

- Going back re-evaluates all conditions, so conditional questions that were
  shown or hidden because of a gating answer respond correctly.
- Going back on the very first question is a no-op (the history is empty, so
  nothing is popped and the same question is re-asked).

### `_GoBackRequest`

```python
from tui_forms.renderer.base import _GoBackRequest
```

A sentinel exception.
Raise it from any `_ask_*` method when the user types the back command.
Do not catch it—`_ask_questions` handles it automatically.

### `_BACK_COMMAND`

```python
_BACK_COMMAND: str = "<"
```

The string the user must type to trigger back navigation.
Compare stripped user input against `self._BACK_COMMAND` (do not hard-code `"<"`).
Override the attribute to change the command.

### Implementation pattern

```python
from tui_forms.renderer.base import BaseRenderer, _GoBackRequest

class MyRenderer(BaseRenderer):
    def _ask_string(self, question, default, prefix) -> str:
        # 1. Show the prompt
        print(f"\n{prefix}{question.title}")
        # 2. Optionally display back hint
        if back_hint := self._back_hint():
            print(f"  ({back_hint})")
        # 3. Read input
        default_str = str(default) if default is not None else ""
        value = input(f"  [{default_str}] " if default_str else "  ").strip()
        # 4. Raise _GoBackRequest when the user types the back command
        if value == self._BACK_COMMAND:
            raise _GoBackRequest()
        return value if value else default_str
```

Apply the same pattern in `_ask_boolean`, `_ask_choice`, and `_ask_multiple`.

---

(basequestion-attributes)=
## BaseQuestion attributes

The `question` argument passed to all abstract methods is a `BaseQuestion` instance.
The following attributes are available to every renderer.

| Attribute | Type | Description |
|---|---|---|
| `key` | `str` | The field key, used as the answer dict key. |
| `type` | `str` | The field type (for example, `"string"`, `"boolean"`, `"array"`). |
| `title` | `str` | The human-readable label to display as the prompt. |
| `description` | `str` | Optional hint text shown below the title. May be an empty string. |
| `default` | `Any` | The raw default from the schema (before {term}`Jinja2` rendering and before pre-populated answer lookup). Use the resolved `default` argument passed to the abstract method instead. |
| `options` | `list[QuestionOption] \| None` | Available choices for `_ask_choice` and `_ask_multiple`. `None` for other types. |
| `required` | `bool` | `True` if the field is listed in the top-level `required` array of the schema. The pipeline calls `_validation_error` and re-prompts when the answer is empty (`""`, `[]`, or `None`). |
| `validator` | `AnswerValidator \| None` | A callable `(value: str) -> bool \| raises ValidationError` that validates free-text input. `None` if no validation is defined. The pipeline calls `_validation_error` and re-prompts automatically when validation fails. |

## QuestionOption

Each entry in `question.options` is a `TypedDict` with two keys:

| Key | Type | Description |
|---|---|---|
| `const` | `Any` | The stored value returned when this option is selected. |
| `title` | `str` | The human-readable label shown to the user. |

```python
# Example: iterating over options in _ask_choice
for i, opt in enumerate(question.options or [], 1):
    print(f"  {i}. {opt['title']}")  # display label
    # opt["const"] is what you return when this option is chosen
```

---

## Question class hierarchy

The following class tree shows all question types.
The concrete `question` argument passed to each abstract method is always an instance of one of the leaf classes.

```
BaseQuestion
├── Question              free-text string, integer, or number input
│   ├── QuestionBoolean   yes/no input; default_value() returns bool
│   ├── QuestionChoice    single-choice; default_value() normalises list → scalar
│   └── QuestionMultiple  multiple-choice; default_value() always returns a list
└── QuestionHidden        never shown to the user; resolved after all user-facing questions
    ├── QuestionConstant  returns raw default unchanged—no Jinja2 rendering
    └── QuestionComputed  renders default as a Jinja2 template (str, list, or dict)
```

`type: object` questions are not a separate class—they use `BaseQuestion` with `subquestions` set.
The pipeline recurses into subquestions without calling any abstract method on the object itself.

---

(jinja2-configuration)=
## Jinja2 configuration

The optional `config` constructor argument lets you customise the {term}`Jinja2` environment used to render default templates.
Pass a dict with a `jinja2_environment` key whose value is forwarded as keyword arguments to `jinja2.Environment`.

```python
from tui_forms.parser import jsonschema_to_form
from tui_forms.renderer.stdlib import StdlibRenderer

frm = jsonschema_to_form(schema)
renderer = StdlibRenderer(
    frm,
    config={
        "jinja2_environment": {
            "variable_start_string": "[[",
            "variable_end_string": "]]",
        }
    },
)
answers = renderer.render()
```

The `autoescape` keyword is always forced to `True` and cannot be overridden through `config`.

`config` is only available when constructing a renderer directly.
{func}`tui_forms.create_renderer` does not currently expose this parameter.
