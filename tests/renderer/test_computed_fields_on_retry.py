"""Tests for issue #17: computed fields must be recalculated after review retry.

When the user completes the form, declines the summary, and changes a value
that a computed field depends on, the computed field must reflect the new value.

See: https://github.com/collective/tui-forms/issues/17
     https://github.com/plone/cookieplone/issues/160
"""

from tui_forms import form


def test_computed_field_recalculated_after_retry(make_form, render_stdlib):
    """When the user changes an answer on retry, computed fields that depend
    on it should reflect the new value."""
    frm = make_form(
        form.Question(
            key="project_slug",
            type="string",
            title="Project Slug",
            description="",
            default="my-project",
        ),
        form.QuestionComputed(
            key="folder_name",
            type="string",
            title="Folder Name",
            description="",
            default="{{ project_slug }}",
        ),
    )
    # Pass 1: answer "slug-1", decline summary ("n")
    # Pass 2: answer "slug-2", accept summary ("y")
    result = render_stdlib(frm, ["slug-1", "n", "slug-2", "y"], confirm=True)
    assert result["project_slug"] == "slug-2"
    assert result["folder_name"] == "slug-2"


def test_computed_field_unchanged_when_dependency_unchanged(make_form, render_stdlib):
    """When the user accepts the same answer on retry, computed fields should
    retain their value."""
    frm = make_form(
        form.Question(
            key="project_slug",
            type="string",
            title="Project Slug",
            description="",
            default="my-project",
        ),
        form.QuestionComputed(
            key="folder_name",
            type="string",
            title="Folder Name",
            description="",
            default="{{ project_slug }}",
        ),
    )
    # Pass 1: answer "slug-1", decline summary ("n")
    # Pass 2: press Enter (accept "slug-1" default), accept summary ("y")
    result = render_stdlib(frm, ["slug-1", "n", "", "y"], confirm=True)
    assert result["project_slug"] == "slug-1"
    assert result["folder_name"] == "slug-1"


def test_chained_computed_fields_recalculated(make_form, render_stdlib):
    """Computed fields that depend on other computed fields should be
    recalculated correctly on retry."""
    frm = make_form(
        form.Question(
            key="title",
            type="string",
            title="Title",
            description="",
            default="My Project",
        ),
        form.QuestionComputed(
            key="slug",
            type="string",
            title="Slug",
            description="",
            default="{{ title | lower | replace(' ', '-') }}",
        ),
        form.QuestionComputed(
            key="folder",
            type="string",
            title="Folder",
            description="",
            default="{{ slug }}",
        ),
    )
    # Pass 1: "Alpha Beta", decline ("n")
    # Pass 2: "Gamma Delta", accept ("y")
    result = render_stdlib(frm, ["Alpha Beta", "n", "Gamma Delta", "y"], confirm=True)
    assert result["title"] == "Gamma Delta"
    assert result["slug"] == "gamma-delta"
    assert result["folder"] == "gamma-delta"


def test_issue_17_reproduction(make_form, render_stdlib):
    """Exact reproduction scenario from the issue description."""
    frm = make_form(
        form.Question(
            key="title",
            type="string",
            title="Project Title",
            description="",
            default="My Project",
        ),
        form.Question(
            key="project_slug",
            type="string",
            title="Project Slug",
            description="",
            default="{{ title | lower | replace(' ', '-') }}",
        ),
        form.QuestionComputed(
            key="__folder_name",
            type="string",
            title="Folder Name",
            description="",
            default="{{ project_slug }}",
        ),
    )
    # Pass 1: accept title default, answer slug="slug-1", decline ("n")
    # Pass 2: accept title default, answer slug="slug-2", accept ("y")
    result = render_stdlib(frm, ["", "slug-1", "n", "", "slug-2", "y"], confirm=True)
    assert result["project_slug"] == "slug-2"
    assert result["__folder_name"] == "slug-2"


def test_hidden_field_recalculated_after_retry(make_form, render_stdlib):
    """QuestionHidden (non-computed) should also be recalculated on retry."""
    frm = make_form(
        form.Question(
            key="name",
            type="string",
            title="Name",
            description="",
            default="Alice",
        ),
        form.QuestionHidden(
            key="greeting",
            type="string",
            title="Greeting",
            description="",
            default="Hello {{ name }}",
        ),
    )
    # Pass 1: "Bob", decline ("n")
    # Pass 2: "Charlie", accept ("y")
    result = render_stdlib(frm, ["Bob", "n", "Charlie", "y"], confirm=True)
    assert result["name"] == "Charlie"
    assert result["greeting"] == "Hello Charlie"
