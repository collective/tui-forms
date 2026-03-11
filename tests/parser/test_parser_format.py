"""Tests for format-based question class selection and built-in format validators."""

from tui_forms import form
from tui_forms.parser import _data_url_validator
from tui_forms.parser import _date_validator
from tui_forms.parser import _datetime_validator
from tui_forms.parser import _email_validator
from tui_forms.parser import jsonschema_to_form

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _schema(*properties: tuple[str, dict]) -> dict:
    """Build a minimal schema containing the given (key, prop) pairs."""
    return {"title": "T", "properties": dict(properties)}


def _parse_one(key: str, prop: dict) -> form.BaseQuestion:
    """Parse a schema with a single property and return that question."""
    frm = jsonschema_to_form(_schema((key, prop)))
    return frm.questions[0]


# ---------------------------------------------------------------------------
# format: computed  →  QuestionComputed
# ---------------------------------------------------------------------------


def test_format_computed_string_produces_question_computed():
    """`type: string, format: computed` should parse to QuestionComputed."""
    q = _parse_one("x", {"type": "string", "format": "computed", "default": "v"})
    assert isinstance(q, form.QuestionComputed)


def test_format_computed_is_hidden():
    """`format: computed` question should be hidden."""
    q = _parse_one("x", {"type": "string", "format": "computed", "default": "v"})
    assert q.hidden is True


def test_format_computed_stores_standard_type():
    """`format: computed` question should carry the declared base type, not 'computed'."""
    q = _parse_one("x", {"type": "string", "format": "computed", "default": "v"})
    assert q.type == "string"


def test_format_computed_has_no_validator():
    """`format: computed` questions must not have a validator."""
    q = _parse_one("x", {"type": "string", "format": "computed", "default": "v"})
    assert q.validator is None


# ---------------------------------------------------------------------------
# format: constant  →  QuestionConstant
# ---------------------------------------------------------------------------


def test_format_constant_string_produces_question_constant():
    """`type: string, format: constant` should parse to QuestionConstant."""
    q = _parse_one("x", {"type": "string", "format": "constant", "default": "v"})
    assert isinstance(q, form.QuestionConstant)


def test_format_constant_array_produces_question_constant():
    """`type: array, format: constant` should parse to QuestionConstant."""
    q = _parse_one("x", {"type": "array", "format": "constant", "default": ["a", "b"]})
    assert isinstance(q, form.QuestionConstant)


def test_format_constant_is_hidden():
    """`format: constant` question should be hidden."""
    q = _parse_one("x", {"type": "string", "format": "constant", "default": "v"})
    assert q.hidden is True


def test_format_constant_stores_standard_type():
    """`format: constant` question should carry the declared base type."""
    q = _parse_one("x", {"type": "string", "format": "constant", "default": "v"})
    assert q.type == "string"


# ---------------------------------------------------------------------------
# format: email
# ---------------------------------------------------------------------------


def test_format_email_produces_question():
    """`format: email` should parse to a regular Question."""
    q = _parse_one("e", {"type": "string", "format": "email"})
    assert isinstance(q, form.Question)
    assert not isinstance(q, form.QuestionComputed)
    assert not isinstance(q, form.QuestionConstant)


def test_format_email_attaches_validator():
    """`format: email` should attach an email validator."""
    q = _parse_one("e", {"type": "string", "format": "email"})
    assert q.validator is not None


@pytest.mark.parametrize(
    "value",
    [
        "user@example.com",
        "user.name+tag@sub.domain.org",
        "a@b.co",
    ],
)
def test_email_validator_accepts_valid(value):
    """_email_validator should return True for valid email addresses."""
    assert _email_validator(value) is True


@pytest.mark.parametrize(
    "value",
    [
        "notanemail",
        "missing@tld",
        "@nodomain.com",
        "spaces in@email.com",
        "",
    ],
)
def test_email_validator_rejects_invalid(value):
    """_email_validator should return False for invalid email addresses."""
    assert _email_validator(value) is False


# ---------------------------------------------------------------------------
# format: date
# ---------------------------------------------------------------------------


def test_format_date_attaches_validator():
    """`format: date` should attach a date validator."""
    q = _parse_one("d", {"type": "string", "format": "date"})
    assert q.validator is not None


@pytest.mark.parametrize(
    "value",
    ["2024-01-15", "2000-12-31", "1999-06-01"],
)
def test_date_validator_accepts_valid(value):
    """_date_validator should return True for valid ISO dates."""
    assert _date_validator(value) is True


@pytest.mark.parametrize(
    "value",
    ["2024-13-01", "2024-00-01", "not-a-date", "2024/01/15", "20240115", ""],
)
def test_date_validator_rejects_invalid(value):
    """_date_validator should return False for invalid date strings."""
    assert _date_validator(value) is False


# ---------------------------------------------------------------------------
# format: date-time
# ---------------------------------------------------------------------------


def test_format_datetime_attaches_validator():
    """`format: date-time` should attach a date-time validator."""
    q = _parse_one("dt", {"type": "string", "format": "date-time"})
    assert q.validator is not None


@pytest.mark.parametrize(
    "value",
    [
        "2024-01-15T10:30:00",
        "2024-01-15T10:30:00+02:00",
        "2024-01-15",
    ],
)
def test_datetime_validator_accepts_valid(value):
    """_datetime_validator should return True for valid ISO 8601 date-time strings."""
    assert _datetime_validator(value) is True


@pytest.mark.parametrize(
    "value",
    ["not-a-datetime", "2024-13-01T00:00:00", ""],
)
def test_datetime_validator_rejects_invalid(value):
    """_datetime_validator should return False for invalid date-time strings."""
    assert _datetime_validator(value) is False


# ---------------------------------------------------------------------------
# format: data-url
# ---------------------------------------------------------------------------


def test_format_data_url_attaches_validator():
    """`format: data-url` should attach a file-existence validator."""
    q = _parse_one("f", {"type": "string", "format": "data-url"})
    assert q.validator is not None


def test_data_url_validator_accepts_existing_file(tmp_path):
    """_data_url_validator should return True for a path to an existing file."""
    f = tmp_path / "file.txt"
    f.write_text("hello")
    assert _data_url_validator(str(f)) is True


def test_data_url_validator_rejects_missing_file():
    """_data_url_validator should return False for a path that does not exist."""
    assert _data_url_validator("/nonexistent/path/file.txt") is False


def test_data_url_validator_rejects_directory(tmp_path):
    """_data_url_validator should return False for a directory path."""
    assert _data_url_validator(str(tmp_path)) is False


# ---------------------------------------------------------------------------
# No validator for unrecognised / absent formats
# ---------------------------------------------------------------------------


def test_no_format_produces_no_validator():
    """A property without a format should have no validator."""
    q = _parse_one("x", {"type": "string"})
    assert q.validator is None


def test_unknown_format_produces_no_validator():
    """An unrecognised format (e.g. 'hostname') should produce no validator."""
    q = _parse_one("x", {"type": "string", "format": "hostname"})
    assert q.validator is None


# ---------------------------------------------------------------------------
# validator key — dotted import path for custom validators
# ---------------------------------------------------------------------------


def test_validator_key_attaches_loaded_callable():
    """A 'validator' key with a valid dotted path should attach that callable."""
    import os.path

    q = _parse_one("x", {"type": "string", "validator": "os.path.isfile"})
    assert q.validator is os.path.isfile


def test_validator_key_overrides_format_validator():
    """An explicit 'validator' key should override the format-based validator."""
    import os.path

    # format: email would normally attach _email_validator; the explicit
    # validator key should win instead.
    q = _parse_one(
        "x", {"type": "string", "format": "email", "validator": "os.path.isfile"}
    )
    assert q.validator is os.path.isfile


def test_empty_validator_key_produces_no_validator():
    """An empty string 'validator' value should be treated as no validator."""
    q = _parse_one("x", {"type": "string", "validator": ""})
    assert q.validator is None


def test_validator_key_ignored_for_computed_fields():
    """A 'validator' key on a computed hidden field should be silently ignored."""
    q = _parse_one(
        "x",
        {
            "type": "string",
            "format": "computed",
            "default": "v",
            "validator": "os.path.isfile",
        },
    )
    assert q.validator is None


def test_validator_key_ignored_for_constant_fields():
    """A 'validator' key on a constant hidden field should be silently ignored."""
    q = _parse_one(
        "x",
        {
            "type": "string",
            "format": "constant",
            "default": "v",
            "validator": "os.path.isfile",
        },
    )
    assert q.validator is None


def test_invalid_validator_key_raises_value_error():
    """A 'validator' key with a bad dotted path should raise ValueError at parse time."""
    with pytest.raises(ValueError, match="dotted path"):
        _parse_one("x", {"type": "string", "validator": "nodot"})


# ---------------------------------------------------------------------------
# options array format
# ---------------------------------------------------------------------------


def test_options_list_produces_choice_question():
    """A property with an 'options' list-of-pairs is parsed as QuestionChoice."""
    q = _parse_one(
        "lang",
        {
            "type": "string",
            "default": "en",
            "options": [["en", "English"], ["de", "Deutsch"]],
        },
    )
    assert isinstance(q, form.QuestionChoice)
    assert q.options == [
        {"const": "en", "title": "English"},
        {"const": "de", "title": "Deutsch"},
    ]


def test_options_list_default_is_respected():
    """The 'default' value on an options-list field is passed through unchanged."""
    q = _parse_one(
        "env",
        {
            "type": "string",
            "default": "prod",
            "options": [["dev", "Dev"], ["prod", "Prod"]],
        },
    )
    assert q.default == "prod"


def test_options_list_with_tuple_items():
    """Tuple items in the 'options' list are also accepted."""
    q = _parse_one(
        "x",
        {
            "type": "string",
            "default": "a",
            "options": [("a", "Alpha"), ("b", "Beta")],
        },
    )
    assert q.options == [
        {"const": "a", "title": "Alpha"},
        {"const": "b", "title": "Beta"},
    ]


def test_options_list_ignored_when_oneOf_present():
    """oneOf takes priority over the 'options' key when both are present."""
    q = _parse_one(
        "x",
        {
            "type": "string",
            "default": "a",
            "oneOf": [{"const": "a", "title": "Alpha"}],
            "options": [["b", "Beta"]],
        },
    )
    assert q.options == [{"const": "a", "title": "Alpha"}]
