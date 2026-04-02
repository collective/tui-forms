"""Tests for issue #16: go-back should retain user-entered values as defaults.

When the user goes back to a previous question, the answer they entered before
should be shown as the default — not the original schema default.

See: https://github.com/collective/tui-forms/issues/16
     https://github.com/plone/cookieplone/issues/159
"""


def test_go_back_shows_previous_answer_as_default(make_form, render_form_capture_input):
    """After going back, the prompt should show the user's previous answer,
    not the schema default."""
    frm = make_form({
        "properties": {
            "version": {
                "type": "string",
                "title": "Version",
                "default": "1.0.0",
            },
            "name": {"type": "string", "title": "Name", "default": ""},
        }
    })
    # Answer "2.0.0", advance, go back, press Enter (accept previous), answer name
    result, prompts = render_form_capture_input(frm, ["2.0.0", "<", "", "Alice"])
    assert result["version"] == "2.0.0"
    # The first prompt for version shows schema default [1.0.0]
    assert "[1.0.0]" in prompts[0]
    # The second prompt for version (after go-back) should show [2.0.0]
    version_prompts = [p for p in prompts if "2.0.0" in p or "1.0.0" in p]
    assert any("2.0.0" in p for p in version_prompts), (
        f"Expected user's previous answer '2.0.0' in prompts, got: {version_prompts}"
    )


def test_go_back_enter_accepts_previous_answer(make_form, render_form):
    """Pressing Enter after going back should accept the user's previous answer."""
    frm = make_form({
        "properties": {
            "version": {
                "type": "string",
                "title": "Version",
                "default": "1.0.0",
            },
            "name": {"type": "string", "title": "Name", "default": ""},
        }
    })
    result = render_form(frm, ["custom", "<", "", "Alice"])
    assert result["version"] == "custom"
    assert result["name"] == "Alice"


def test_go_back_can_change_previous_answer(make_form, render_form):
    """Going back and typing a new value should replace the previous answer."""
    frm = make_form({
        "properties": {
            "version": {
                "type": "string",
                "title": "Version",
                "default": "1.0.0",
            },
            "name": {"type": "string", "title": "Name", "default": ""},
        }
    })
    result = render_form(frm, ["2.0.0", "<", "3.0.0", "Alice"])
    assert result["version"] == "3.0.0"
    assert result["name"] == "Alice"


def test_go_back_retains_choice_value(make_form, render_form):
    """After going back, a choice question should show the previous selection
    as the default."""
    frm = make_form({
        "properties": {
            "license": {
                "type": "string",
                "title": "License",
                "default": "mit",
                "oneOf": [
                    {"const": "mit", "title": "MIT"},
                    {"const": "gpl", "title": "GPL"},
                    {"const": "apache", "title": "Apache"},
                ],
            },
            "name": {"type": "string", "title": "Name", "default": ""},
        }
    })
    # Select GPL (2), advance, go back, press Enter (accept GPL), answer name
    result = render_form(frm, ["2", "<", "", "Alice"])
    assert result["license"] == "gpl"
    assert result["name"] == "Alice"


def test_go_back_retains_boolean_value(make_form, render_form):
    """After going back, a boolean question should keep the user's previous answer."""
    frm = make_form({
        "properties": {
            "use_docker": {
                "type": "boolean",
                "title": "Use Docker?",
                "default": False,
            },
            "name": {"type": "string", "title": "Name", "default": ""},
        }
    })
    # Answer "y" (True), advance, go back, press Enter (accept True), answer name
    result = render_form(frm, ["y", "<", "", "Alice"])
    assert result["use_docker"] is True
    assert result["name"] == "Alice"


def test_go_back_retains_multiple_values(make_form, render_form):
    """After going back, a multiple-choice question should keep previous selections."""
    frm = make_form({
        "properties": {
            "extras": {
                "type": "array",
                "title": "Extras",
                "default": ["a"],
                "items": {
                    "oneOf": [
                        {"const": "a", "title": "Alpha"},
                        {"const": "b", "title": "Beta"},
                        {"const": "c", "title": "Charlie"},
                    ]
                },
            },
            "name": {"type": "string", "title": "Name", "default": ""},
        }
    })
    # Select Beta,Charlie (2,3), advance, go back, press Enter (accept previous), answer name
    result = render_form(frm, ["2,3", "<", "", "Alice"])
    assert result["extras"] == ["b", "c"]
    assert result["name"] == "Alice"


def test_go_back_retains_answer_for_conditional_evaluation(make_form, render_form):
    """The gating answer should remain so conditional questions stay visible
    after going back and re-accepting the same gating value."""
    frm = make_form({
        "properties": {
            "provider": {
                "type": "string",
                "title": "Provider",
                "default": "local",
                "oneOf": [
                    {"const": "local", "title": "Local"},
                    {"const": "oidc", "title": "OIDC"},
                ],
            },
            "name": {"type": "string", "title": "Name", "default": ""},
        },
        "allOf": [
            {
                "if": {"properties": {"provider": {"const": "oidc"}}},
                "then": {
                    "properties": {
                        "oidc_url": {
                            "type": "string",
                            "title": "OIDC URL",
                            "default": "",
                        }
                    }
                },
            }
        ],
    })
    # Choose "oidc" (2), answer url, go back to url, press Enter (keep url),
    # answer name
    result = render_form(frm, ["2", "https://id.example.com", "<", "", "Alice"])
    assert result["provider"] == "oidc"
    assert result["oidc_url"] == "https://id.example.com"
    assert result["name"] == "Alice"


def test_issue_16_reproduction(make_form, render_form):
    """Exact reproduction scenario from the issue description."""
    frm = make_form({
        "properties": {
            "title": {
                "type": "string",
                "title": "Project Title",
                "default": "My Project",
            },
            "version": {
                "type": "string",
                "title": "Version",
                "default": "1.0.0",
            },
            "description": {
                "type": "string",
                "title": "Description",
                "default": "",
            },
        }
    })
    # Answer title, answer version="custom-version", go back from description,
    # press Enter on version (should keep "custom-version"), answer description
    result = render_form(
        frm, ["My Project", "custom-version", "<", "", "A description"]
    )
    assert result["title"] == "My Project"
    assert result["version"] == "custom-version"
    assert result["description"] == "A description"
