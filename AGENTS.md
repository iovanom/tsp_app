Agents Guide for this repo
Python 3.12; uv-managed (uv.lock present).
Install dev deps: `uv sync --group dev`.
Run all tests: `pytest -q`.
Run one file: `pytest tests/test_graph.py -q`.
Run one test: `pytest tests/test_graph.py::test_construct_minimal_and_defaults -q`.
Filter tests by expr: `pytest -k "pattern" -q`.
Format (write): `black . && isort .`.
Lint (check-only): `black --check . && isort --check-only . && flake8`.
Build package: `uv build`.
Run CLI: `uv run tsp`.
Formatting: Black 100 cols; isort profile=black, line_length=100.
Flake8: honor `.flake8` (80 cols); keep new code ≤80 to pass.
Imports: group stdlib/third-party/first-party; prefer absolute `tsp...`; no wildcards.
Types: prefer `list[str]`, unions with `|`, and `T | None`; file-level `type` aliases OK.
Naming: snake_case for funcs/vars, PascalCase for classes, UPPER_SNAKE for constants.
Errors: validate inputs; raise ValueError/IndexError with clear messages; avoid bare except/log-and-continue.
Tests: place in `tests/`; use `tempfile` for files and clean up.
Cursor/Copilot rules: none found in this repo.
Commits: small, focused; avoid changing tool configs unless required.