from tui_forms import form
from tui_forms.parser import jsonschema_to_form


def test_override_property_with_condition():
    """Test that a property defined in properties can be made conditional in allOf."""
    schema = {
        "properties": {
            "feature_x": {"type": "boolean", "default": True},
            "conditional_q": {"type": "string", "default": "always shown"},
        },
        "allOf": [
            {
                "if": {"properties": {"feature_x": {"const": True}}},
                "then": {
                    "properties": {
                        "conditional_q": {
                            "type": "string",
                            "default": "only if feature_x is true",
                            "description": "updated description",
                        }
                    }
                },
            }
        ],
    }
    frm = jsonschema_to_form(schema)
    q = next(q for q in frm.questions if q.key == "conditional_q")

    # Current behavior: condition is None because it was already in seen_keys
    # Desired behavior: condition is set
    assert q.condition == [{"key": "feature_x", "value": True}]
    assert q.description == "updated description"
    assert q.default == "only if feature_x is true"


def test_hide_property_conditionally_via_computed():
    """Test that a property can be hidden (made computed) conditionally."""
    schema = {
        "properties": {
            "feature_x": {"type": "boolean", "default": True},
            "conditional_q": {"type": "string", "default": "always shown"},
        },
        "allOf": [
            {
                "if": {"properties": {"feature_x": {"const": False}}},
                "then": {
                    "properties": {
                        "conditional_q": {
                            "type": "string",
                            "format": "computed",
                            "default": "hidden now",
                        }
                    }
                },
            }
        ],
    }
    frm = jsonschema_to_form(schema)
    q = next(q for q in frm.questions if q.key == "conditional_q")

    # If feature_x is False, it should use the computed version.
    # Actually, in tui-forms, a question with a condition is SKIPPED if condition not met.
    # Here, if feature_x is True, the condition False is NOT met, so the question is skipped?
    # No, the question IS in properties, so it has a base definition.

    # If we allow overriding, we have a problem: which one applies when?
    # tui-forms currently has a static list of questions.

    # If we want it to be Asked when X is true, and Computed when X is false,
    # we might need two different entries in the questions list, both with conditions.

    # But wait, JSONSchema doesn't allow two properties with the same name in the same object.
    # However, allOf can have multiple properties with same name.

    # If tui-forms wants to support this, it might need to allow multiple entries for the same key
    # and the renderer should pick the active one.
    # But currently Form.answers is a dict, and record() overwrites.

    # If we have multiple questions with same key, only one should be active at a time.

    assert q.condition == [{"key": "feature_x", "value": False}]
    assert isinstance(q, form.QuestionComputed)
