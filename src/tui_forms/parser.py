from collections.abc import Callable
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


def _check_min_length(value: str, limit: int) -> None:
    if len(value) < limit:
        plural = "s" if limit != 1 else ""
        raise form.ValidationError(f"Must be at least {limit} character{plural}.")


def _check_max_length(value: str, limit: int) -> None:
    if len(value) > limit:
        plural = "s" if limit != 1 else ""
        raise form.ValidationError(f"Must be at most {limit} character{plural}.")


def _check_pattern(value: str, pattern: str) -> None:
    if not re.fullmatch(pattern, value):
        raise form.ValidationError(f"Must match pattern: {pattern}.")


def _check_minimum(value: str, limit: float) -> None:
    try:
        num = float(value)
    except ValueError:
        raise form.ValidationError(f"Must be a number \u2265 {limit}.") from None
    if num < limit:
        raise form.ValidationError(f"Must be \u2265 {limit}.")


def _check_maximum(value: str, limit: float) -> None:
    try:
        num = float(value)
    except ValueError:
        raise form.ValidationError(f"Must be a number \u2264 {limit}.") from None
    if num > limit:
        raise form.ValidationError(f"Must be \u2264 {limit}.")


_KW_CHECKERS: dict[str, Callable[[str, Any], None]] = {
    "minLength": _check_min_length,
    "maxLength": _check_max_length,
    "pattern": _check_pattern,
    "minimum": _check_minimum,
    "maximum": _check_maximum,
}


def _build_keyword_validator(
    prop_schema: dict[str, Any],
) -> form.AnswerValidator | None:
    """Build a validator that enforces JSONSchema constraint keywords.

    Recognises ``minLength``, ``maxLength``, ``pattern`` (strings) and
    ``minimum``, ``maximum`` (integers / numbers).  Returns ``None`` when none
    of these keywords are present in *prop_schema*.
    """
    checks: list[tuple[str, Any]] = [
        (kw, prop_schema[kw])
        for kw in ("minLength", "maxLength", "pattern", "minimum", "maximum")
        if kw in prop_schema
    ]

    if not checks:
        return None

    def _validator(value: str) -> bool:
        for kw, limit in checks:
            _KW_CHECKERS[kw](value, limit)
        return True

    return _validator


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


def _extract_enum_options(prop_schema: dict[str, Any]) -> list[form.QuestionOption]:
    """Build options from a bare ``enum`` list, with optional ``enumNames`` labels."""
    enum_names: list[str] = prop_schema.get("enumNames", [])
    return [
        {"const": val, "title": enum_names[i] if i < len(enum_names) else str(val)}
        for i, val in enumerate(prop_schema["enum"])
    ]


def _extract_any_of_options(any_of: list[Any]) -> list[form.QuestionOption]:
    """Build options from an ``anyOf`` block (each entry has ``enum`` + ``title``)."""
    options: list[form.QuestionOption] = []
    for item in any_of:
        if "enum" in item and "title" in item:
            for val in item["enum"]:
                options.append({"const": val, "title": item["title"]})
    return options


def _extract_options(
    prop_schema: dict[str, Any], schema: dict[str, Any]
) -> list[form.QuestionOption]:
    """Extract QuestionOptions from oneOf, anyOf, options, or enum entries."""
    if one_of := prop_schema.get("oneOf"):
        return [
            {"const": item["const"], "title": item["title"]}
            for item in one_of
            if "const" in item and "title" in item
        ]
    if any_of := prop_schema.get("anyOf"):
        return _extract_any_of_options(any_of)
    if raw_options := prop_schema.get("options"):
        return [
            {"const": item[0], "title": item[1]}
            for item in raw_options
            if isinstance(item, (list, tuple)) and len(item) >= 2
        ]
    if "enum" in prop_schema:
        return _extract_enum_options(prop_schema)
    items = prop_schema.get("items")
    if isinstance(items, dict):
        return _extract_options(items, schema)
    return []


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


def _find_insert_index(subquestions: list[form.BaseQuestion], gating_key: str) -> int:
    """Return the index right after the gating question, or len(subquestions).

    When multiple conditional blocks share the same gating key, each batch
    is inserted after the previous one, preserving allOf declaration order.

    :param subquestions: The current list of questions.
    :param gating_key: The key of the question that gates the conditional.
    :return: The insertion index.
    """
    last_index = len(subquestions)
    for i, q in enumerate(subquestions):
        if q.key == gating_key:
            last_index = i + 1
    # Also skip past any conditionals already inserted for this gating key.
    while last_index < len(subquestions) and subquestions[last_index].condition:
        last_index += 1
    return last_index


def _build_subquestions(
    prop_schema: dict[str, Any], schema: dict[str, Any]
) -> list[form.BaseQuestion]:
    """Build subquestions for an object-type property.

    Collects direct property subquestions, then inserts conditional
    subquestions from allOf/if/then blocks right after their gating
    question, skipping duplicate keys.
    """
    subquestions: list[form.BaseQuestion] = []
    seen_keys: set[str] = set()
    required_keys: list[str] = prop_schema.get("required", [])

    for sub_key, sub_prop in prop_schema.get("properties", {}).items():
        subquestions.append(
            _parse_property(
                sub_key, sub_prop, schema, required=sub_key in required_keys
            )
        )
        seen_keys.add(sub_key)

    for allof_item in prop_schema.get("allOf", []):
        then = allof_item.get("then")
        if not then:
            continue
        if "$ref" in then:
            then = _resolve_ref(schema, then["$ref"])
        question_condition = _extract_condition(allof_item.get("if", {}))
        then_required: list[str] = then.get("required", [])
        gating_key = question_condition[0]["key"] if question_condition else ""
        insert_at = _find_insert_index(subquestions, gating_key)
        for sub_key, sub_prop in then.get("properties", {}).items():
            if sub_key not in seen_keys:
                sq = _parse_property(
                    sub_key,
                    sub_prop,
                    schema,
                    condition=question_condition,
                    required=sub_key in then_required,
                )
                subquestions.insert(insert_at, sq)
                insert_at += 1
                seen_keys.add(sub_key)

    return subquestions


def _parse_property(
    key: str,
    prop_schema: dict[str, Any],
    schema: dict[str, Any],
    condition: list[form.Condition] | None = None,
    required: bool = False,
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

    if prop_format not in _HIDDEN_FORMATS:
        keyword_validator = _build_keyword_validator(prop_schema)
        if keyword_validator is not None:
            if validator is not None:
                # Compose: keyword constraints run first, then the explicit validator.
                _explicit = validator
                _kw_captured: form.AnswerValidator = keyword_validator

                def _composed(
                    value: str,
                    _kw: form.AnswerValidator = _kw_captured,
                    _ex: form.AnswerValidator = _explicit,
                ) -> bool:
                    _kw(value)
                    return _ex(value)

                validator = _composed
            else:
                validator = keyword_validator

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
        required=required,
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
    questions = _build_subquestions(schema, schema)
    return form.Form(
        title=title, description=description, questions=questions, root_key=root_key
    )
