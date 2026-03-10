"""Tests for tui_forms.utils.validators.load_validator."""

from tui_forms.utils.validators import load_validator

import pytest


# ---------------------------------------------------------------------------
# Successful load
# ---------------------------------------------------------------------------


def test_load_stdlib_callable():
    """load_validator should return the callable at a valid dotted path."""
    func = load_validator("os.path.isfile")
    import os.path

    assert func is os.path.isfile


def test_loaded_callable_is_callable():
    """The returned object must be callable."""
    func = load_validator("os.path.isfile")
    assert callable(func)


def test_load_function_from_tui_forms():
    """load_validator should work with paths inside the tui_forms package."""
    func = load_validator("tui_forms.parser._email_validator")
    assert callable(func)
    assert func("user@example.com") is True


# ---------------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "path",
    [
        "nodot",
        "alsono",
        "x",
    ],
)
def test_no_dot_raises_value_error(path):
    """A path without a dot should raise ValueError."""
    with pytest.raises(ValueError, match="dotted path"):
        load_validator(path)


def test_nonexistent_module_raises_value_error():
    """An unimportable module path should raise ValueError."""
    with pytest.raises(ValueError, match="Cannot import validator module"):
        load_validator("nonexistent_xyz_module.func")


def test_nonexistent_attribute_raises_value_error():
    """A missing attribute on a valid module should raise ValueError."""
    with pytest.raises(ValueError, match="has no attribute"):
        load_validator("os.path.nonexistent_function_xyz")


def test_non_callable_attribute_raises_value_error():
    """A non-callable attribute should raise ValueError."""
    # os.sep is a str constant, not callable
    with pytest.raises(ValueError, match="is not callable"):
        load_validator("os.sep")
