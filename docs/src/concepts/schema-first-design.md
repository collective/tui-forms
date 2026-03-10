---
myst:
  html_meta:
    "description": "An explanation of why TUI Forms uses JSONSchema as its form definition language and what that design decision enables."
    "property=og:description": "An explanation of why TUI Forms uses JSONSchema as its form definition language and what that design decision enables."
    "property=og:title": "Schema-first design"
    "keywords": "tui-forms, JSONSchema, design, architecture, schema-first, concepts"
---

# Schema-first design

TUI Forms takes a declarative, schema-first approach: you define what your form looks like in data, and the library handles the rest.
This page explains why that choice was made and what it enables.

## The problem

Most CLI tools and terminal scaffolding utilities ask questions by writing imperative code:
call `input()`, check the value, branch, call `input()` again.
This approach works for a handful of questions, but it does not scale.
As the form grows, the logic for defaults, validation, conditional questions, and output formatting becomes tangled with the I/O code.
Switching the output style—say, from plain `input()` to a styled `rich` prompt—requires rewriting or duplicating the entire interaction flow.

## The solution

TUI Forms separates the *definition* of a form from its *rendering*.
You describe the form once in a {term}`JSONSchema` document—field names, types, titles, defaults, choices, and conditions.
TUI Forms reads that document, builds an internal `Form` object, and hands it to a renderer.
The renderer is responsible only for I/O; it knows nothing about the schema.

This mirrors the design of {term}`react-jsonschema-form`, which applies the same principle to web forms.
TUI Forms brings it to the terminal.

## What it enables

**Renderer independence.**
Because the form definition is separate from I/O, you can swap renderers without touching the schema.
The same schema works with the zero-dependency `stdlib` renderer, the styled `rich` renderer, or any custom renderer you write.

**Reuse and composition.**
{term}`JSONSchema` supports `$ref` and `$defs`, so you can define option lists and field groups once and reference them in multiple places.
A shared schema can power multiple tools.

**Familiar tooling.**
{term}`JSONSchema` is a widely adopted standard.
Schema files can be validated, documented, and edited with existing tooling, without any knowledge of TUI Forms internals.

**Computed and conditional fields.**
Because all field metadata lives in the schema, TUI Forms can apply {term}`Jinja2` templates to defaults and evaluate `if/then` conditions in a single, predictable pass—after all user-facing questions have been answered.
No branching logic leaks into your application code.

## The rendering pipeline

When you call `renderer.render()`, TUI Forms follows a fixed two-phase pipeline regardless of the renderer backend:

1. **User-facing phase.**
   Each non-hidden question is asked in schema order.
   Conditional questions (from `allOf/if/then`) are skipped when their condition is not satisfied.
   The `default` of each question is rendered as a {term}`Jinja2` template against the answers collected so far.

2. **Hidden phase.**
   After all user input is collected, hidden fields are resolved in order.
   `QuestionConstant` fields return their raw value.
   `QuestionComputed` fields render their `default` template against the full set of answers.

The renderer receives the final flat dict of answers.
It never needs to implement this logic itself.

## Trade-offs

The schema-first approach works best when your form structure is known ahead of time and can be expressed in {term}`JSONSchema`.
It is not designed for highly dynamic forms where the set of questions depends on runtime state that cannot be captured in a schema.
For those cases, using {term}`BaseRenderer` directly and managing the `Form` object yourself gives you full control.
