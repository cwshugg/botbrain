---
name: "documentation"
description: "Best practices for writing documentation"
applyTo: "**"
---

# Best Practices in Documentation

Documentation is an important piece of a software project.
It should be concise, but present all information necessary for a high-level understanding from an onlooker who is not familiar with the project.

## The Laws of Documentation

One very important factor to writing good documentation is being **terse**.
*Always* live by these Laws of Terseness:

### 1. The Law of Terseness

**More words == more mental fatigue.**

Documentation should always be written in the best interest of the humans reading it.
Keep descriptions as short as possible without losing any meaning!
The true measure of good documentation is how well meaning can be conveyed with as few words as possible.

(For more information on terseness, please read the [terseness instructions](./terseness.instructions.md).)

### 2. The Law of Jargon

**More jargon used == more confusion.**

Certain terminology may be needed when writing specific documentation.
That being said, always use as few jargon-like words and buzzwords as possible.
The more jargon present, the harder it will be for somebody to understand.
Always write documentation such that somebody *completely unfamiliar* to the project can read it to gain understanding.

### 3. The Law of Cleanliness

**A badly-formatted document is difficult to absorb.**

Always create meaningful divisions and headings to organize the words in a document.
Humans and agents alike benefit most from documentation when it is approachable and well organized.

For example: don't cram explanations into one giant paragraph.
Instead, split it up into brief sections with `## Markdown Headings` to separate concepts.

### 4. The Law of Consistency

**Names and special strings should always be formatted the same way throughout documentation.**

When formatting **Important Names**, `file-names.md`, `code_symbols()`, and more, always format them the exact same throughout documentation.

### 5. The Law of Linking

**Links make documentation easier to navigate.**

Markdown and other documentation formats support hyperlinks.
Always use these to point to other files when referencing other concepts written in separate files.
Prefer linking across many files rather than maintaining one or two massive files.

### 6. The Law of Small Files

**Large files never get fully read through.**

The key to writing documentation that people will actually *read* is to keep each individual document short.
Always divide up concepts into separate files where it makes sense.
When describing those concepts, keep the file small.

If you need to describe a sub-concept in detail, often times you can split this into a second file.
Then, use the **Law of Linking** to link those documents together for easy navigation.

## Documenting New Changes

When writing documentation for new additions or changes, ensure all new changes are properly documented in the existing documentation.
Focus on updating the documentation to describe the *current behavior* only; avoid making notes about previous or upcoming changes.

For user-facing APIs, CLI commands, configuration options, defaults, error behavior, or examples, compare the documentation with the implemented source of truth.
Do not describe planned or removed behavior as available; implement it, remove it, or qualify the documentation.
Execute examples when the project provides a practical way to do so.

## File Structure

Unless otherwise requested, please create documentation under `docs/` directory at the top of the project's file tree.
Individual files should describe individual concepts.
If needed, you may create sub-directories underneath `docs/` to better organize documentation into groups.

## Documentation Format

Unless otherwise requested, please write documentation in markdown (`.md`).
See the [markdown instructions](./markdown.instructions.md) to learn how to write effective markdown.

## Diagrams

When creating diagrams, use mermaid flowcharts rather than ASCII art, when possible.
See the [mermaid syntax reference](https://mermaid.ai/open-source/intro/syntax-reference.html) for more information.

