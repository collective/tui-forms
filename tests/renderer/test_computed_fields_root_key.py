"""Tests for issue #17: computed fields with root_key must be recalculated on retry.

When a form uses ``root_key``, answers are nested under that key.  The filter
that strips computed fields before a retry pass must operate on the inner dict,
not the top-level wrapper — otherwise stale computed values leak through.

See: https://github.com/collective/tui-forms/issues/17
"""


def test_computed_field_recalculated_with_root_key(make_form, render_form):
    """Computed field under root_key must reflect the updated answer on retry."""
    frm = make_form(
        {
            "properties": {
                "project_slug": {
                    "type": "string",
                    "title": "Project Slug",
                    "default": "my-project",
                },
                "__folder_name": {
                    "type": "string",
                    "title": "Folder Name",
                    "format": "computed",
                    "default": "{{ cookiecutter.project_slug }}",
                },
            }
        },
        root_key="cookiecutter",
    )
    # Pass 1: answer "slug-1", decline summary ("n")
    # Pass 2: answer "slug-2", accept summary ("y")
    result = render_form(frm, ["slug-1", "n", "slug-2", "y"], confirm=True)
    assert result["cookiecutter"]["project_slug"] == "slug-2"
    assert result["cookiecutter"]["__folder_name"] == "slug-2"


def test_computed_field_unchanged_with_root_key(make_form, render_form):
    """Computed field keeps its value when the dependency doesn't change."""
    frm = make_form(
        {
            "properties": {
                "project_slug": {
                    "type": "string",
                    "title": "Project Slug",
                    "default": "my-project",
                },
                "__folder_name": {
                    "type": "string",
                    "title": "Folder Name",
                    "format": "computed",
                    "default": "{{ cookiecutter.project_slug }}",
                },
            }
        },
        root_key="cookiecutter",
    )
    # Pass 1: "slug-1", decline ("n")
    # Pass 2: accept default ("slug-1"), accept ("y")
    result = render_form(frm, ["slug-1", "n", "", "y"], confirm=True)
    assert result["cookiecutter"]["project_slug"] == "slug-1"
    assert result["cookiecutter"]["__folder_name"] == "slug-1"


def test_chained_computed_fields_with_root_key(make_form, render_form):
    """Chained computed fields under root_key recalculate correctly on retry."""
    frm = make_form(
        {
            "properties": {
                "title": {
                    "type": "string",
                    "title": "Title",
                    "default": "My Project",
                },
                "slug": {
                    "type": "string",
                    "title": "Slug",
                    "format": "computed",
                    "default": "{{ cc.title | lower | replace(' ', '-') }}",
                },
                "folder": {
                    "type": "string",
                    "title": "Folder",
                    "format": "computed",
                    "default": "{{ cc.slug }}",
                },
            }
        },
        root_key="cc",
    )
    # Pass 1: "Alpha Beta", decline ("n")
    # Pass 2: "Gamma Delta", accept ("y")
    result = render_form(frm, ["Alpha Beta", "n", "Gamma Delta", "y"], confirm=True)
    assert result["cc"]["title"] == "Gamma Delta"
    assert result["cc"]["slug"] == "gamma-delta"
    assert result["cc"]["folder"] == "gamma-delta"
