---
myst:
  html_meta:
    "description": "Why TUI Forms documentation is structured the way it is, and how to find what you need."
    "property=og:description": "Why TUI Forms documentation is structured the way it is, and how to find what you need."
    "property=og:title": "Documentation structure"
    "keywords": "tui-forms, documentation, Diátaxis, structure, how-to, reference, concepts, tutorials"
---

# Documentation structure

This page explains why the TUI Forms documentation is organised the way it is,
and how to navigate it depending on what you need.

## The framework: Diátaxis

The TUI Forms documentation follows the {term}`Diátaxis` framework,
which organises documentation into four distinct types based on what the reader needs to *do*:

| Type | Oriented towards | Answers the question |
|---|---|---|
| **Tutorials** | Learning | *"Can you teach me?"* |
| **How-to guides** | Specific goals | *"How do I...?"* |
| **Reference** | Information lookup | *"What does X do?"* |
| **Concepts** | Understanding | *"Why does it work this way?"* |

Each type serves a different reader in a different situation.
Mixing them—for example, writing explanations inside a reference page—makes documentation harder to use.
Diátaxis keeps them separate so you can find what you need without reading everything.

## Why Diátaxis?

Documentation that grows organically tends to blur these boundaries.
A "guide" might start with a tutorial, drift into explanation, and end with an API reference—useful to the author who wrote it, but disorienting to the reader who arrives mid-task.

By committing to Diátaxis from the start, TUI Forms documentation stays navigable as it grows.
Each page has a single purpose, and the section it lives in tells you what to expect before you read a word.

## What each section contains

### Tutorials

*Not yet written.*

Tutorials walk a complete beginner through a self-contained learning experience.
The goal is understanding, not production use—a tutorial may simplify or omit details to keep the reader moving.

### How-to guides

Practical, task-oriented instructions for readers who already know the basics and need to accomplish a specific goal.
Each guide starts from a concrete problem and ends when the problem is solved.

Current guides:

- {doc}`/how-to-guides/use-in-project`: install TUI Forms and render your first form
- {doc}`/how-to-guides/create-renderer`: implement a custom renderer backend
- {doc}`/how-to-guides/contribute`: set up a development environment and submit changes

### Reference

Technical descriptions of every supported construct, class, and method.
Reference pages describe the machinery; they do not explain the reasoning behind it or walk you through using it.

Current reference pages:

- {doc}`/reference/jsonschema-support`: which {term}`JSONSchema` constructs TUI Forms recognises
- {doc}`/reference/base-renderer`: the `BaseRenderer` abstract class and its methods
- {doc}`/reference/renderer-stdlib`: how the `stdlib` renderer presents each question type
- {doc}`/reference/renderer-rich`: how the `rich` renderer presents each question type
- {doc}`/reference/renderer-cookiecutter`: how the `cookiecutter` renderer presents each question type

### Concepts

Understanding-oriented pages that explain *why* TUI Forms works the way it does.
Reading a concepts page will not tell you how to accomplish a task,
but it will give you the mental model to work effectively with the library.

Current concepts pages:

- {doc}`schema-first-design`: why TUI Forms uses {term}`JSONSchema` as its form definition language
- {doc}`documentation-structure`: this page

## How to navigate

**If you are new to TUI Forms** and want to get something working quickly, start with {doc}`/how-to-guides/use-in-project`.

**If you have a specific question** such as "how do I add a conditional field?," go to the Reference section and check {doc}`/reference/jsonschema-support`.

**If something is not behaving as you expect** and you want to understand the underlying model, read {doc}`schema-first-design`.

**If you want to extend TUI Forms** with a custom renderer, follow {doc}`/how-to-guides/create-renderer` and use {doc}`/reference/base-renderer` as a look-up resource while you write the code.
