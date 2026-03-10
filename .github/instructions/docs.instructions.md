---
applyTo: "docs/src/**/*.md"
---
# Documentation standards

This codebase is a library that helps developers to build schema-driven form wizards for the terminal

ALWAYS use `TUI Forms` as the friendly name of the package and `tui-forms` when refering to the package codebase.

## 1. Audience and scope

- This library is intended for Python developers building terminal applications or command line utilities.
- About the reader:
  - Could be categorized as:
    - **End User**: Python developer willing to use this library in their own projects.
    - **Contributor**: Also a Python developer, probably also an End User, but someone willing to contribute to this library by fixing issues, implementing new features, and writing documentation.
  - Assume they know: Python development terms, Python 3.12+
  - Do NOT assume they know: internal architecture decisions, the history of the project, or even other libraries providing the same features.
- Full documentation lives at: https://collective.github.io/tui-forms

---

## 2. Documentation structure (Diátaxis)

All documentation must fit one of these four types. Never mix types in the same file.

| Type | Purpose | Answers |
|---|---|---|
| **Tutorial** | Learning-oriented, step-by-step | "How do I get started?" |
| **How-to guide** | Task-oriented, goal-focused | "How do I accomplish X?" |
| **Reference** | Information-oriented, API/config | "What does parameter X do?" |
| **Explanation** | Understanding-oriented, concepts | "Why does it work this way?" |

When drafting a new file, STATE which type it is at the top of your working notes before writing.

---

## 3. File metadata (REQUIRED on every file)

Every `.md` file must begin with a MyST metadata block. Use this template and fill in accurate values — do not copy the placeholder text verbatim into the output:

```markdown
---
myst:
  html_meta:
    "description": "[PLACEHOLDER: one sentence, plain English, no marketing language]"
    "property=og:description": "[PLACEHOLDER: same as description above]"
    "property=og:title": "[PLACEHOLDER: page title, matches the H1 heading below]"
    "keywords": "[PLACEHOLDER: comma-separated, include library name, relevant concepts]"
---
```

Rules:
- `description` must be a single sentence under 160 characters.
- `keywords` must include `tui-forms` as the first keyword.
- The `og:title` must exactly match the H1 heading of the page.
- NEVER copy example metadata from another page without updating all four fields.

---

## 4. Toolchain

- **Documentation framework**: Sphinx with MyST-Parser (Markdown)
- **Setup environment**: `make install`
- **Build command**: `make docs-html`
- **Live preview**: `make docs-livehtml`
- **Output directory**: `docs/_build/html`
- **Hosting**: `GitHub Pages`

Before suggesting any Sphinx extension or MyST feature, verify it is listed in `docs/src/conf.py`. Do not assume extensions are available.

---

## 5. Writing standards (Vale-enforced)

Vale is configured for **American English** with the following style guides active:
- Microsoft

Vale runs via: `make docs-vale`

Rules that Vale does NOT catch but must still be followed:

- Use second-person voice ("you", not "the user" or "one").
- Use active voice. Passive voice is allowed only when the actor is genuinely unknown.
- Use present tense ("returns a string", not "will return a string").
- Sentence case for all headings ("Getting started", not "Getting Started"). Exception: proper nouns and the library name.
- One sentence per line in the source Markdown (makes diffs readable).
- No filler phrases: "simply", "just", "easily", "obviously", "of course".
- Spell out acronyms on first use per page, even common ones.

---

## 6. Code examples

- ALL code examples must be tested and working against the current version.
- Use `tui_forms` as the import in all examples.
- Show the minimal working example first, then add complexity.
- Every code block must have a language tag:
  ````markdown
  ```python
  ```
  ````
- If an example requires setup not shown inline, reference the relevant how-to guide explicitly.
- NEVER fabricate API behaviour. If unsure whether a method exists or behaves a certain way, read the source at `src/tui_forms` before writing.

---

## 7. MyST-specific syntax

Use MyST directives correctly. Prefer these patterns:

**Notes and warnings:**
```markdown
:::{note}
Use notes sparingly — only for information the reader would otherwise miss.
:::

:::{warning}
Reserve warnings for actions that could cause data loss or security issues.
:::
```

**Cross-references** (always use labels, never bare URLs for internal links):
```markdown
{doc}`/path/to/page`
{ref}`label-name`
{py:func}`yourlibrary.module.function`
```

**Do not use** raw HTML unless there is no MyST equivalent.

---

## 8. What to verify before writing

Before drafting any documentation:

1. Read the relevant source files in `src/tui_forms`.
2. Check whether existing documentation already covers the topic (`docs/src`).
3. Run the build to confirm there are no pre-existing errors: `make docs-html`.

FORBIDDEN: "I think this method does...", "It should...", "Probably..."
REQUIRED: "According to `[file:line]`...", "The source shows..."

If the behaviour is not clear from the source, STATE: "I cannot confirm this from the source code — please verify."

---

## 9. Definition of done

A documentation task is complete only when:

- [ ] Vale passes with zero errors: `make docs-vale`
- [ ] Sphinx builds with zero warnings: `make docs-html`
- [ ] All internal cross-references resolve.
- [ ] All code examples have been run and produce the stated output.
- [ ] Metadata block is present and accurate on every new or modified file.
- [ ] The page fits exactly one Diátaxis type.

"The page renders" is not done. "Vale passes" is not done on its own. All six must be true.

---

## 10. What not to do

- NEVER mix tutorial and reference content in the same page.
- NEVER use the word "simply" or "just" (Vale will catch this, but be proactive).
- NEVER document behaviour you have not verified in the source.
- NEVER copy metadata from another page without updating all fields.
