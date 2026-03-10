Added `root_key` support on `create_renderer` and `Form`.
When set, all answers are nested under the given key in the returned dict (e.g. `{"cookiecutter": {...}}`).
Jinja2 default templates reference answers using `{{ root_key.answer_key }}` syntax. @ericof
