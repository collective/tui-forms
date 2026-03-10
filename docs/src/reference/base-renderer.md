---
myst:
  html_meta:
    "description": "API reference for BaseRenderer — the abstract base class that all TUI Forms renderer backends extend."
    "property=og:description": "API reference for BaseRenderer — the abstract base class that all TUI Forms renderer backends extend."
    "property=og:title": "BaseRenderer reference"
    "keywords": "tui-forms, reference, BaseRenderer, API, renderer, abstract, _ask_string, _ask_boolean, _ask_choice, _ask_multiple"
---

# BaseRenderer

`BaseRenderer` is the abstract base class that all TUI Forms renderer backends extend.
It lives in `tui_forms.renderer.base`.

The class provides the complete rendering pipeline — question ordering, condition evaluation, {term}`Jinja2` default rendering, and hidden-field resolution — while delegating all terminal I/O to five abstract methods that each concrete renderer must implement.

## Class definition

```python
class BaseRenderer(ABC):
    name: str = "base"
```

Set `name` to a unique string identifier on your subclass.
This value is used when the renderer is discovered via `available_renderers()`.

## Constructor

```python
def __init__(self, frm: form.Form, config: dict[str, Any] | None = None) -> None
```

| Parameter | Type | Description |
|---|---|---|
| `frm` | `form.Form` | The parsed form to render. Produced by `jsonschema_to_form` or `create_renderer`. |
| `config` | `dict \| None` | Optional {term}`Jinja2` environment configuration. See [Jinja2 configuration](#jinja2-configuration) below. |

You do not normally call this directly — use {func}`tui_forms.create_renderer` instead.

## Public method

### `render`

```python
def render(self) -> dict[str, Any]
```

Run the form interactively and return the collected answers.

Calls the abstract methods in order as the user progresses through the form.
After all user-facing questions are answered, resolves hidden fields automatically.

**Returns:** A flat `dict` mapping each question `key` to its answer.
When `root_key` was set on the form, all answers are nested under that key.

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
| `default` | `Any` | The pre-rendered default value, or `None` if no default was set. |
| `prefix` | `str` | Progress prefix (e.g. `"[1/5] "`) to display before the question title. |

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
| `default` | `bool \| None` | `True`, `False`, or `None` if no default was set. |
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
| `default` | `Any` | The `const` value of the pre-selected option, or `""` if none. |
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
| `default` | `list` | The list of `const` values that are pre-selected. May be empty. |
| `prefix` | `str` | Progress prefix. |

**Returns:** A `list` of `const` values for the selected options.

---

### `_validation_error`

```python
@abstractmethod
def _validation_error(self, question: BaseQuestion) -> None
```

Display an error message when the user's answer fails the field's validator.
Called automatically by the rendering pipeline before re-prompting the question.

| Parameter | Type | Description |
|---|---|---|
| `question` | `BaseQuestion` | The question whose answer failed validation. |

---

## Overridable method

### `_format_prefix`

```python
def _format_prefix(self, current: int, total: int) -> str
```

Return the progress prefix prepended to each question title.
The default implementation returns `"[current/total] "` (e.g. `"[3/9] "`).

Override this method to change the format or return `""` to suppress the prefix.

| Parameter | Type | Description |
|---|---|---|
| `current` | `int` | 1-based index of the current question. |
| `total` | `int` | Total number of user-facing questions. |

**Returns:** A `str` prefix, or `""` to show no prefix.

---

## BaseQuestion attributes

The `question` argument passed to all abstract methods is a `BaseQuestion` instance.
The following attributes are available to every renderer.

| Attribute | Type | Description |
|---|---|---|
| `key` | `str` | The field key, used as the answer dict key. |
| `type` | `str` | The field type (e.g. `"string"`, `"boolean"`, `"array"`). |
| `title` | `str` | The human-readable label to display as the prompt. |
| `description` | `str` | Optional hint text shown below the title. May be an empty string. |
| `default` | `Any` | The raw default from the schema (before {term}`Jinja2` rendering). Use the pre-rendered `default` argument instead. |
| `options` | `list[QuestionOption] \| None` | Available choices for `_ask_choice` and `_ask_multiple`. `None` for other types. |
| `validator` | `AnswerValidator \| None` | A callable `(value: str) -> bool` that validates free-text input. `None` if no validation is defined. The pipeline calls `_validation_error` and re-prompts automatically when validation fails. |

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
    ├── QuestionConstant  returns raw default unchanged — no Jinja2 rendering
    └── QuestionComputed  renders default as a Jinja2 template (str, list, or dict)
```

`type: object` questions are not a separate class — they use `BaseQuestion` with `subquestions` set.
The pipeline recurses into subquestions without calling any abstract method on the object itself.

---

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
