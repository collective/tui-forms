---
myst:
  html_meta:
    "description": "Reference for the TUI Forms public API: create_form, create_renderer, get_renderer, and available_renderers."
    "property=og:description": "Reference for the TUI Forms public API: create_form, create_renderer, get_renderer, and available_renderers."
    "property=og:title": "Public API reference"
    "keywords": "tui-forms, reference, API, create_form, create_renderer, get_renderer, available_renderers"
---

# Public API reference

All public functions are importable directly from `tui_forms`.

```python
from tui_forms import available_renderers, create_form, create_renderer, get_renderer
```

---

(fn-create_form)=
## `create_form`

```python
def create_form(schema: dict[str, Any], root_key: str = "") -> Form
```

Parse a JSON Schema dict and return a `Form` instance.

| Parameter | Type | Description |
|---|---|---|
| `schema` | `dict` | The already-loaded JSON Schema dict describing the form. |
| `root_key` | `str` | Optional key to nest all answers under in the returned dict. Defaults to `""` (no nesting). |

**Returns:** A `Form` instance ready to pass to a renderer constructor.

**Raises:** `jsonschema.ValidationError` if the schema does not conform to the expected form structure.

Use `create_form` when you need the `Form` object before you decide which renderer to use, or when you want to inspect or reuse the form across multiple renderers.

```python
from tui_forms import create_form, get_renderer

frm = create_form(schema, root_key="cookiecutter")
renderer = get_renderer("rich")(frm)
answers = renderer.render()
```

---

(fn-create_renderer)=
## `create_renderer`

```python
def create_renderer(
    renderer: str,
    schema: dict[str, Any],
    root_key: str = "",
    jinja_config: dict[str, Any] | None = None,
    jinja_extensions: list[str] | None = None,
) -> BaseRenderer
```

Parse a schema and return an initialised renderer in one step.

| Parameter | Type | Description |
|---|---|---|
| `renderer` | `str` | Name of the renderer (for example `"stdlib"`, `"rich"`, `"noinput"`). |
| `schema` | `dict` | The already-loaded JSON Schema dict describing the form. |
| `root_key` | `str` | Optional key to nest all answers under in the returned dict. |
| `jinja_config` | `dict \| None` | Optional {term}`Jinja2` environment configuration forwarded to the renderer. |
| `jinja_extensions` | `list[str] \| None` | Optional list of {term}`Jinja2` extensions to load. |

**Returns:** An initialised `BaseRenderer` instance ready to call `render()` on.

**Raises:**
- `ValueError` if the renderer name is not registered.
- `jsonschema.ValidationError` if the schema is invalid.

```python
from tui_forms import create_renderer

renderer = create_renderer("rich", schema)
answers = renderer.render()
```

---

(fn-get_renderer)=
## `get_renderer`

```python
def get_renderer(renderer: str) -> type[BaseRenderer]
```

Return the renderer *class* for the given name without instantiating it.

| Parameter | Type | Description |
|---|---|---|
| `renderer` | `str` | Name of the renderer to look up. |

**Returns:** The renderer class (a subclass of `BaseRenderer`).

**Raises:** `ValueError` if the renderer name is not registered.

Use `get_renderer` together with `create_form` when you need to control construction yourself—for example, to pass a custom `config` or to reuse the same form with multiple renderer instances.

```python
from tui_forms import create_form, get_renderer

frm = create_form(schema)
klass = get_renderer("stdlib")
renderer = klass(frm)
answers = renderer.render()
```

---

(fn-available_renderers)=
## `available_renderers`

```python
def available_renderers() -> dict[str, type[BaseRenderer]]
```

Return all registered renderers.

**Returns:** A `dict` mapping each renderer name to its class.
Use this to inspect which renderers are available at runtime or to build dynamic renderer selection.

```python
from tui_forms import available_renderers

for name, klass in available_renderers().items():
    print(name, klass)
```
