from tui_forms.renderer.base import BaseRenderer
from tui_forms.renderer.stdlib import StdlibRenderer

import pytest


@pytest.fixture
def renderer_klass() -> type[BaseRenderer]:
    """Return the renderer class being tested.

    Defaults to StdlibRenderer. Overridden in test_rich.py and
    test_cookiecutter.py to test those specific renderers.
    """
    return StdlibRenderer
