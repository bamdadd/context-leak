# Contributing to context-leak

Thanks for your interest. This is a research repo; correctness and
reproducibility come before features. All scenario data is synthetic and
invented — never add real customer or patient data.

## Setup
```bash
uv sync
uv run pre-commit install
```

Run: `pre-commit install` (or `uv run ruff format .` before pushing) — CI enforces ruff format and will fail otherwise.

## Before you open a PR
- `uv run ruff check . && uv run ruff format --check .`
- `uv run mypy src`
- `uv run pytest -q`
- New behaviour needs a test. Success is programmatically verified, never
  LLM-judged (see [docs/DESIGN.md](docs/DESIGN.md)).

## Good first issues
See the [`good first issue`](https://github.com/bamdadd/context-leak/issues?q=is%3Aopen+label%3A%22good+first+issue%22)
label for small, self-contained tasks with acceptance criteria and file
pointers. If the tracker is empty, open an issue describing what you'd like to
add and we'll scope it together.

## Reproducibility rules
- Pin versions (the `uv.lock` is committed; the pre-commit hook revs match it).
- Any results table states the models, seeds, and wall-clock.
