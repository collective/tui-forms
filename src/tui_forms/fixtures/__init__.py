"""Pytest plugin fixtures for testing tui-forms based wizards."""

from tui_forms.fixtures._protocols import MakeForm
from tui_forms.fixtures._protocols import MakeQuestions
from tui_forms.fixtures._protocols import RenderForm
from tui_forms.fixtures._protocols import RenderFormCaptureInput


__all__ = [
    "MakeForm",
    "MakeQuestions",
    "RenderForm",
    "RenderFormCaptureInput",
]
