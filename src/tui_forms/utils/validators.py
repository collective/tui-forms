from importlib import import_module
from tui_forms.form.question import AnswerValidator


def load_validator(dotted_path: str) -> AnswerValidator:
    """Load and return a validator callable from a dotted Python import path.

    The callable must accept a single ``str`` argument and return a ``bool``.
    It is loaded at schema-parse time so that missing or misspelled paths fail
    immediately rather than at runtime.

    :param dotted_path: Dotted import path of the form ``module.callable``
        (e.g. ``mypackage.validators.is_valid_slug``).
    :raises ValueError: If the path has no dot, the module cannot be imported,
        the attribute does not exist, or the resolved object is not callable.
    :return: The callable found at the given path.
    """
    if "." not in dotted_path:
        raise ValueError(
            f"Invalid validator path {dotted_path!r}: expected a dotted path "
            f"of the form 'module.callable'."
        )
    module_path, attr_name = dotted_path.rsplit(".", 1)
    try:
        module = import_module(module_path)
    except ImportError as exc:
        raise ValueError(
            f"Cannot import validator module {module_path!r}: {exc}"
        ) from exc
    try:
        validator = getattr(module, attr_name)
    except AttributeError as exc:
        raise ValueError(
            f"Module {module_path!r} has no attribute {attr_name!r}."
        ) from exc
    if not callable(validator):
        raise ValueError(f"{dotted_path!r} is not callable.")
    return validator
