from tui_forms.form import form
from tui_forms.parser import jsonschema_to_form

import jsonschema
import pytest


@pytest.mark.parametrize(
    "filename",
    [
        "cookieplone.json",
        "plone-distribution.json",
        "rjsf-arrays.json",
        "rjsf-enum-objects.json",
        "rjsf-if-then-else.json",
        "rjsf-large.json",
        "rjsf-nested.json",
        "rjsf-pattern-properties.json",
        "rjsf-simple.json",
    ],
)
def test_valid_schema_parses_without_error(load_schema, filename):
    """A valid schema should parse without raising."""
    schema = load_schema(filename)
    new_form = jsonschema_to_form(schema)
    assert isinstance(new_form, form.Form)


@pytest.mark.parametrize(
    "invalid_schema",
    [
        {"questions": {}},  # missing properties
        {"title": "My Form"},  # missing properties
        ["not", "an", "object"],  # missing properties
        {"title": 42, "properties": {}},  # title must be a string
    ],
)
def test_invalid_schema_raises(invalid_schema):
    """Schemas missing required fields or of wrong type should raise ValidationError."""
    with pytest.raises(jsonschema.ValidationError):
        jsonschema_to_form(invalid_schema)
