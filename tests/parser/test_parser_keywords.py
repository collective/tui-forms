"""Tests for JSONSchema constraint keywords: minLength, maxLength, pattern,
minimum, maximum, enum, and enumNames."""

from tui_forms import form
from tui_forms.form.question import ValidationError
from tui_forms.parser import jsonschema_to_form

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _parse_one(key: str, prop: dict) -> form.BaseQuestion:
    """Parse a schema with a single property and return that question."""
    frm = jsonschema_to_form({"title": "T", "properties": {key: prop}})
    return frm.questions[0]


def _assert_valid(q: form.BaseQuestion, value: str) -> None:
    assert q.validator is not None
    assert q.validator(value) is True


def _assert_invalid(q: form.BaseQuestion, value: str, match: str = "") -> None:
    assert q.validator is not None
    with pytest.raises(ValidationError, match=match):
        q.validator(value)


# ---------------------------------------------------------------------------
# minLength
# ---------------------------------------------------------------------------


def test_min_length_valid():
    q = _parse_one("x", {"type": "string", "minLength": 3})
    _assert_valid(q, "abc")
    _assert_valid(q, "abcd")


def test_min_length_exact_boundary_valid():
    q = _parse_one("x", {"type": "string", "minLength": 3})
    _assert_valid(q, "abc")


def test_min_length_too_short_raises():
    q = _parse_one("x", {"type": "string", "minLength": 3})
    _assert_invalid(q, "ab", match="at least 3 character")


def test_min_length_one_character_message():
    q = _parse_one("x", {"type": "string", "minLength": 1})
    _assert_invalid(q, "", match="at least 1 character")


# ---------------------------------------------------------------------------
# maxLength
# ---------------------------------------------------------------------------


def test_max_length_valid():
    q = _parse_one("x", {"type": "string", "maxLength": 5})
    _assert_valid(q, "hi")
    _assert_valid(q, "hello")


def test_max_length_exact_boundary_valid():
    q = _parse_one("x", {"type": "string", "maxLength": 5})
    _assert_valid(q, "hello")


def test_max_length_too_long_raises():
    q = _parse_one("x", {"type": "string", "maxLength": 5})
    _assert_invalid(q, "toolong", match="at most 5 character")


# ---------------------------------------------------------------------------
# pattern
# ---------------------------------------------------------------------------


def test_pattern_valid():
    q = _parse_one("x", {"type": "string", "pattern": "^[a-z]+$"})
    _assert_valid(q, "hello")


def test_pattern_invalid_raises():
    q = _parse_one("x", {"type": "string", "pattern": "^[a-z]+$"})
    _assert_invalid(q, "Hello123", match="Must match pattern")


def test_pattern_error_includes_pattern():
    q = _parse_one("x", {"type": "string", "pattern": "^[a-z]+$"})
    with pytest.raises(ValidationError, match=r"Must match pattern"):
        q.validator("BAD")  # type: ignore[misc]


# ---------------------------------------------------------------------------
# minimum
# ---------------------------------------------------------------------------


def test_minimum_valid():
    q = _parse_one("x", {"type": "integer", "minimum": 10})
    _assert_valid(q, "10")
    _assert_valid(q, "100")


def test_minimum_exact_boundary_valid():
    q = _parse_one("x", {"type": "integer", "minimum": 10})
    _assert_valid(q, "10")


def test_minimum_below_raises():
    q = _parse_one("x", {"type": "integer", "minimum": 10})
    _assert_invalid(q, "9", match=r"≥ 10")


def test_minimum_non_numeric_raises():
    q = _parse_one("x", {"type": "integer", "minimum": 10})
    _assert_invalid(q, "abc", match="Must be a number")


# ---------------------------------------------------------------------------
# maximum
# ---------------------------------------------------------------------------


def test_maximum_valid():
    q = _parse_one("x", {"type": "integer", "maximum": 100})
    _assert_valid(q, "100")
    _assert_valid(q, "50")


def test_maximum_exact_boundary_valid():
    q = _parse_one("x", {"type": "integer", "maximum": 100})
    _assert_valid(q, "100")


def test_maximum_above_raises():
    q = _parse_one("x", {"type": "integer", "maximum": 100})
    _assert_invalid(q, "101", match=r"≤ 100")


def test_maximum_non_numeric_raises():
    q = _parse_one("x", {"type": "integer", "maximum": 100})
    _assert_invalid(q, "abc", match="Must be a number")


# ---------------------------------------------------------------------------
# minimum + maximum together
# ---------------------------------------------------------------------------


def test_min_max_combined_valid():
    q = _parse_one("x", {"type": "integer", "minimum": 1, "maximum": 10})
    _assert_valid(q, "5")


def test_min_max_combined_below_raises():
    q = _parse_one("x", {"type": "integer", "minimum": 1, "maximum": 10})
    _assert_invalid(q, "0", match=r"≥ 1")


def test_min_max_combined_above_raises():
    q = _parse_one("x", {"type": "integer", "minimum": 1, "maximum": 10})
    _assert_invalid(q, "11", match=r"≤ 10")


# ---------------------------------------------------------------------------
# Keyword validator composition with explicit validator
# ---------------------------------------------------------------------------


def test_keyword_and_explicit_validator_both_enforced():
    """When a keyword constraint and an explicit format validator are present,
    both must pass."""
    q = _parse_one(
        "x",
        {"type": "string", "format": "email", "minLength": 10},
    )
    # Valid: long enough and a valid email
    _assert_valid(q, "user@example.com")


def test_keyword_fails_before_explicit_validator():
    """The keyword validator runs first; if it fails the explicit one is not called."""
    q = _parse_one(
        "x",
        {"type": "string", "format": "email", "minLength": 20},
    )
    # Too short — keyword raises before email check
    _assert_invalid(q, "a@b.com", match="at least 20 character")


# ---------------------------------------------------------------------------
# Keywords ignored on hidden fields
# ---------------------------------------------------------------------------


def test_keywords_ignored_on_computed_field():
    q = _parse_one(
        "x",
        {"type": "string", "format": "computed", "default": "v", "minLength": 3},
    )
    assert q.validator is None


def test_keywords_ignored_on_constant_field():
    q = _parse_one(
        "x",
        {"type": "string", "format": "constant", "default": "v", "maxLength": 1},
    )
    assert q.validator is None


# ---------------------------------------------------------------------------
# enum (standalone)
# ---------------------------------------------------------------------------


def test_enum_produces_question_choice():
    q = _parse_one("x", {"type": "string", "enum": ["a", "b", "c"]})
    assert isinstance(q, form.QuestionChoice)


def test_enum_options_use_value_as_title():
    q = _parse_one("x", {"type": "string", "enum": ["alpha", "beta"]})
    assert q.options is not None
    assert q.options[0] == {"const": "alpha", "title": "alpha"}
    assert q.options[1] == {"const": "beta", "title": "beta"}


def test_enum_integer_values():
    q = _parse_one("x", {"type": "integer", "enum": [1, 2, 3]})
    assert isinstance(q, form.QuestionChoice)
    assert q.options is not None
    assert q.options[0] == {"const": 1, "title": "1"}


# ---------------------------------------------------------------------------
# enumNames
# ---------------------------------------------------------------------------


def test_enum_names_used_as_titles():
    q = _parse_one(
        "x",
        {
            "type": "string",
            "enum": ["alpha", "beta", "stable"],
            "enumNames": ["Alpha — experimental", "Beta", "Stable"],
        },
    )
    assert q.options is not None
    assert q.options[0] == {"const": "alpha", "title": "Alpha — experimental"}
    assert q.options[1] == {"const": "beta", "title": "Beta"}
    assert q.options[2] == {"const": "stable", "title": "Stable"}


def test_enum_names_shorter_than_enum_falls_back_to_value():
    """When enumNames has fewer entries than enum, extra values use the raw value."""
    q = _parse_one(
        "x",
        {
            "type": "string",
            "enum": ["a", "b", "c"],
            "enumNames": ["Alpha", "Beta"],
        },
    )
    assert q.options is not None
    assert q.options[2] == {"const": "c", "title": "c"}


# ---------------------------------------------------------------------------
# oneOf takes priority over enum
# ---------------------------------------------------------------------------


def test_one_of_takes_priority_over_enum():
    """When both oneOf and enum are present, oneOf wins."""
    q = _parse_one(
        "x",
        {
            "type": "string",
            "oneOf": [{"const": "x", "title": "X title"}],
            "enum": ["ignored"],
        },
    )
    assert q.options is not None
    assert len(q.options) == 1
    assert q.options[0]["title"] == "X title"


# ---------------------------------------------------------------------------
# Showcase schema parses without error
# ---------------------------------------------------------------------------


def test_showcase_schema_parses():
    """The bundled showcase.json demo schema should parse without errors."""
    import json
    from pathlib import Path

    schema_path = (
        Path(__file__).parent.parent.parent
        / "src"
        / "tui_forms"
        / "demo"
        / "showcase.json"
    )
    schema = json.loads(schema_path.read_text())
    frm = jsonschema_to_form(schema)
    assert frm.title == "TUI Forms Feature Showcase"
    keys = [q.key for q in frm.questions]
    assert "project_name" in keys
    assert "stability" in keys
    assert "port" in keys
