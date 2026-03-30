from pathlib import Path
from tui_forms import create_renderer
from typing import Any

import json
import sys


def _get_schema(filename: str = "distribution") -> Path:
    """Get the Path to a demo schema file."""
    path = Path(__file__).parent / f"{filename}.json"
    if not path.is_file():
        raise FileNotFoundError(f"Demo schema file not found: {filename}.json")
    return path


def run_demo(
    renderer: str,
    schema_name: str = "distribution",
    root_key: str = "",
    confirm: bool = False,
) -> dict[str, Any]:
    """Run the demo form using the named renderer.

    Loads the specified demo schema file, parses it into a Form, renders it
    interactively, and prints the collected answers.

    :param renderer: Name of the renderer to use (e.g. ``"stdlib"``, ``"rich"``).
    :param schema_name: Name of the schema file (without .json extension) to load.
    :param root_key: Optional root key to nest all answers under in the final dict.
    :param confirm: When ``True``, show a summary/confirmation screen after all
        questions are answered.
    :return: The answers dict collected from the user.
    """
    schema_file = _get_schema(schema_name)
    schema = json.loads(schema_file.read_text())
    r = create_renderer(renderer, schema, root_key=root_key)
    answers = r.render(confirm=confirm)
    print("\n--- Collected answers ---")
    for key, value in answers.items():
        print(f"  {key}: {value!r}")
    return answers


def main() -> None:
    """Entry point for the demo script."""
    renderer_name = "stdlib"
    schema_name = "distribution"
    root_key = ""
    confirm = "--no-confirm" not in sys.argv
    args = [a for a in sys.argv[1:] if a != "--no-confirm"]
    if len(args) > 0:
        renderer_name = args[0]
    if len(args) > 1:
        schema_name = args[1]
    if schema_name == "cookieplone":
        root_key = "cookiecutter"
    try:
        run_demo(renderer_name, schema_name, root_key=root_key, confirm=confirm)
    except ValueError as e:
        print(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
