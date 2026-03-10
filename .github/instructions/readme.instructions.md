---
applyTo: "README.md"
---
# README file standards

## 1. Audience and scope

- This library is intended for Python developers building terminal applications or command line utilities.
- The README.md file is going to be the first contact the reader has with this project:
  - Will be viewed on GitHub
  - Will be viewed also on PyPI
- The file must:
  - Start with a short tagline and a brief project description.
  - Describe the features with enough detail so the reader understands what each feature does:
    - ✅ (good bullet point wording): `- Different renderers using other Python libraries like rich`
    - ❌ (too vague): `- Renderers`
    - Review the code if necessary to explain features accurately.
  - Include a minimal usage/code example showing how to define a JSONSchema and render a form.
  - Provide installation instructions for end users (using `pip`, `poetry`, and `uv`).
  - Provide installation instructions for developers willing to contribute to this project.
  - End with a license section.
- About the reader:
  - Could be categorized as:
    - **End User**: Python developer willing to use this library in their own projects.
    - **Contributor**: Also a Python developer, probably also an End User, but someone willing to contribute to this library by fixing issues, implementing new features, and writing documentation.
  - Assume they know: Python development terms, Python 3.12+
  - Do NOT assume they know: internal architecture decisions, the history of the project, or even other libraries providing the same features.
- Full documentation lives at: https://collective.github.io/tui-forms

## 2. Suggested README structure

Use this section order:

1. Badges (CI status, PyPI version, license)
2. Project name and tagline
3. Short description (2–4 sentences)
4. Features (bulleted list with enough detail)
5. Usage (minimal code example)
6. Installation (End User)
7. Contributing (Contributor setup)
8. License

## 3. Recommendations

- ALWAYS use `TUI Forms` as the friendly name of the package and `tui-forms` when refering to the package codebase.
- ALWAYS use emojis in section titles for a friendly tone.
- ALWAYS use second person ("you") when addressing the reader.
- End User:
  - Provide installation instructions on how to add this package to their own projects using `pip`, `poetry`, and `uv`.
  - Refer them to the full documentation for usage and how to integrate with their own project.
- Contributor:
  - ALWAYS recommend using `make` commands. The key targets are:
    - `make install` — set up the development environment
    - `make format` — format the codebase
    - `make lint` — run the linter
    - `make lint-mypy` — check type hints
    - `make test` — run all tests
    - `make test-coverage` — run tests with coverage report
    - `make docs-html` — build the HTML documentation
    - `make docs-livehtml` — build and serve documentation locally
  - NEVER recommend using `pip install`, `uv add`, or `uv pip` directly.
