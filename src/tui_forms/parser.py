from datetime import datetime
from pathlib import Path
from tui_forms import form
from tui_forms.utils.validators import load_validator
from typing import Any

import jsonschema
import re


_FORM_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["properties"],
    "properties": {
        "title": {"type": "string"},
        "description": {"type": "string"},
        "properties": {"type": "object"},
    },
}

# Formats that mark a question as hidden; they are handled before type dispatch.
_HIDDEN_FORMATS: frozenset[str] = frozenset({"computed", "constant"})


def _email_validator(value: str) -> bool:
    """Return True if value is a valid email address."""
    return bool(re.match(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$", value))


def _date_validator(value: str) -> bool:
    """Return True if value is a valid ISO 8601 date (YYYY-MM-DD)."""
    try:
        datetime.strptime(value, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def _datetime_validator(value: str) -> bool:
    """Return True if value is a valid ISO 8601 date-time string."""
    try:
        datetime.fromisoformat(value)
        return True
    except ValueError:
        return False


def _data_url_validator(value: str) -> bool:
    """Return True if value is a path to an existing file."""
    return Path(value).is_file()


# Map of format strings to their validator functions.
_FORMAT_VALIDATORS: dict[str, form.AnswerValidator] = {
    "date": _date_validator,
    "date-time": _datetime_validator,
    "data-url": _data_url_validator,
    "email": _email_validator,
    "idn-email": _email_validator,
}


def _resolve_ref(schema: dict[str, Any], ref: str) -> dict[str, Any]:
    """Resolve a $ref pointer within the root schema."""
    parts = ref.lstrip("#/").split("/")
    result = schema
    for part in parts:
        try:
            result = result[part]
        except KeyError as exc:
            raise ValueError(
                f"Cannot resolve $ref {ref!r}: '{part}' not found in schema."
            ) from exc
    return result


def _extract_options(
    prop_schema: dict[str, Any], schema: dict[str, Any]
) -> list[form.QuestionOption]:
    """Extract QuestionOptions from oneOf, anyOf, or options entries."""
    options: list[form.QuestionOption] = []
    if one_of := prop_schema.get("oneOf"):
        options = [
            {"const": item["const"], "title": item["title"]}
            for item in one_of
            if "const" in item and "title" in item
        ]
    elif any_of := prop_schema.get("anyOf"):
        for item in any_of:
            if "enum" in item and "title" in item:
                for val in item["enum"]:
                    options.append({"const": val, "title": item["title"]})
    elif raw_options := prop_schema.get("options"):
        for item in raw_options:
            if isinstance(item, (list, tuple)) and len(item) >= 2:
                options.append({"const": item[0], "title": item[1]})
    elif (items := prop_schema.get("items")) and isinstance(items, dict):
        options = _extract_options(items, schema)
    return options


def _extract_condition(if_block: dict[str, Any]) -> list[form.Condition] | None:
    """Extract all conditions from a JSON Schema if-block.

    Handles the pattern: if: {properties: {key: {const: value}}}
    All property conditions are collected and evaluated with AND logic.
    """
    properties = if_block.get("properties", {})
    conditions: list[form.Condition] = [
        {"key": key, "value": value_schema["const"]}
        for key, value_schema in properties.items()
        if "const" in value_schema
    ]
    return conditions if conditions else None


def _select_question_class(
    prop_type: str,
    prop_format: str,
    options: list[form.QuestionOption] | None,
) -> type[form.BaseQuestion]:
    """Select the appropriate question class for a given type, format, and options.

    The ``format`` field takes precedence: ``format: constant`` produces a
    :class:`QuestionConstant` and ``format: computed`` produces a
    :class:`QuestionComputed`, regardless of the declared ``type``.
    """
    match prop_format:
        case "constant":
            return form.QuestionConstant
        case "computed":
            return form.QuestionComputed
    match prop_type:
        case "boolean":
            return form.QuestionBoolean
        case "array" if options:
            return form.QuestionMultiple
        case _ if options:
            return form.QuestionChoice
    return form.Question


def _build_subquestions(
    prop_schema: dict[str, Any], schema: dict[str, Any]
) -> list[form.BaseQuestion]:
    """Build subquestions for an object-type property.

    Collects direct property subquestions, then appends conditional
    subquestions from allOf/if/then blocks, skipping duplicate keys.
    """
    subquestions: list[form.BaseQuestion] = []
    seen_keys: set[str] = set()

    for sub_key, sub_prop in prop_schema.get("properties", {}).items():
        subquestions.append(_parse_property(sub_key, sub_prop, schema))
        seen_keys.add(sub_key)

    for allof_item in prop_schema.get("allOf", []):
        then = allof_item.get("then")
        if not then:
            continue
        if "$ref" in then:
            then = _resolve_ref(schema, then["$ref"])
        question_condition = _extract_condition(allof_item.get("if", {}))
        for sub_key, sub_prop in then.get("properties", {}).items():
            if sub_key not in seen_keys:
                sq = _parse_property(
                    sub_key, sub_prop, schema, condition=question_condition
                )
                subquestions.append(sq)
                seen_keys.add(sub_key)

    return subquestions


def _parse_property(
    key: str,
    prop_schema: dict[str, Any],
    schema: dict[str, Any],
    condition: list[form.Condition] | None = None,
) -> form.BaseQuestion:
    """Parse a single schema property into a BaseQuestion instance."""
    if "$ref" in prop_schema:
        ref_schema = _resolve_ref(schema, prop_schema["$ref"])
        prop_schema = {
            **ref_schema,
            **{k: v for k, v in prop_schema.items() if k != "$ref"},
        }

    items = prop_schema.get("items")
    if isinstance(items, dict) and "$ref" in items:
        ref_schema = _resolve_ref(schema, items["$ref"])
        prop_schema = {
            **prop_schema,
            "items": {
                **ref_schema,
                **{k: v for k, v in items.items() if k != "$ref"},
            },
        }

    prop_type = prop_schema.get("type", "string")
    prop_format = prop_schema.get("format", "")
    options = _extract_options(prop_schema, schema)
    question_class = _select_question_class(prop_type, prop_format, options)

    subquestions: list[form.BaseQuestion] | None = None
    if prop_type == "object":
        built = _build_subquestions(prop_schema, schema)
        subquestions = built if built else None

    validator: form.AnswerValidator | None = (
        _FORMAT_VALIDATORS.get(prop_format)
        if prop_format not in _HIDDEN_FORMATS
        else None
    )

    if (
        validator_path := prop_schema.get("validator")
    ) and prop_format not in _HIDDEN_FORMATS:
        validator = load_validator(validator_path)

    return question_class(
        key=key,
        type=prop_type,
        title=prop_schema.get("title", key),
        description=prop_schema.get("description", ""),
        default=prop_schema.get("default"),
        options=options,
        subquestions=subquestions,
        condition=condition,
        validator=validator,
    )


def jsonschema_to_form(schema: dict[str, Any], root_key: str = "") -> form.Form:
    """Convert a JSON Schema to a Form instance.

    :param schema: The JSON Schema to convert.
    :param root_key: Optional root key to nest all answers under in the final dict.
    :raises jsonschema.ValidationError: If the schema does not conform to the
        expected form structure.
    :return: The parsed form definition.
    """
    jsonschema.validate(schema, _FORM_SCHEMA)
    title = schema.get("title", "")
    description = schema.get("description", "")
    questions = [
        _parse_property(key, prop_schema, schema)
        for key, prop_schema in schema.get("properties", {}).items()
    ]
    return form.Form(
        title=title, description=description, questions=questions, root_key=root_key
    )
