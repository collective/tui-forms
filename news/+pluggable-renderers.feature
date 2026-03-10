Added a pluggable renderer architecture based on Python entry points (group `tui_forms.renderers`).
Third-party packages can register custom renderers by declaring an entry point — no changes to `tui-forms` itself are needed.
Installed renderers are discovered at runtime via `available_renderers()` and selected by name in `create_renderer()`. @ericof
