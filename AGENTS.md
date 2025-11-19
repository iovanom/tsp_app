Agents Guide for this repo

## Project Overview
This is a Python CLI tool for solving the Traveling Salesman Problem (TSP) using constructive algorithms (nearest neighbor, cheapest insertion) with optional 2-opt improvement. Supports asymmetric cost matrices via CSV input.

## File Structure
- `src/tsp/__init__.py`: CLI entry point with argument parsing and main execution logic.
- `src/tsp/algorithms/constructive.py`: TSP algorithms (nearest_neighbor, cheapest_insertion, two_opt).
- `src/tsp/models/graph.py`: AsymmetricGraph class for cost matrix handling with labels.
- `src/tsp/io/csv_reader.py`: CSV file reader for cost matrices with header labels.
- `tests/test_algorithms.py`: Unit tests for constructive algorithms.
- `tests/test_graph.py`: Unit tests for AsymmetricGraph.
- `tests/test_io_csv_reader.py`: Unit tests for CSV reading.
- `tests/test_two_opt.py`: Unit tests for 2-opt algorithm.
- `samples/minimal_sample.csv`: Small 3-node example (A,B,C).
- `samples/large_sample.csv`: 100-node example (A1-J10 labels).
- `samples/sample.csv`: 25-node example (A-Y labels).
- `README.md`: User documentation with CLI usage and examples.
- `pyproject.toml`: Project configuration (dependencies, build).
- `setup.cfg`: Additional config (flake8, etc.).
- `uv.lock`: Dependency lock file for uv.
- `.flake8`: Flake8 configuration.
- `.gitignore`: Git ignore rules.
- `.python-version`: Python version specification.

## New Features Implemented
- **CLI Options**:
  - `--algorithm {nearest_neighbor,cheapest_insertion}`: Choose constructive algorithm (default: nearest_neighbor).
  - `--benchmark`: Run multiple runs and report stats (min/max/avg cost and time).
  - `--runs N`: Number of benchmark runs (default: 10).
  - `--two-opt`: Apply 2-opt local search improvement after constructive algorithm.
  - `--two-opt-max-passes N`: Max passes for 2-opt (default: 100; ignored if timeout set).
  - `--two-opt-timeout S`: Time limit for 2-opt in seconds (ignores max_passes when set).
- **2-opt Algorithm**: Local search to improve tours by reversing segments that reduce cost; includes safety limits to prevent infinite loops.
- **Sample Files**: Added CSV examples for testing (3, 25, 100 nodes).
- **Benchmarking**: CLI supports performance measurement with stats output.

## Development Guidelines
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

## Agent Tips
- **Adding New Algorithms**: Implement in `src/tsp/algorithms/constructive.py` with signature `def algo(graph: AsymmetricGraph, start: int) -> tuple[list[int], float]`. Add to CLI choices in `__init__.py` and tests in `tests/test_algorithms.py`.
- **CSV Format**: First row: node labels (e.g., A,B,C). Subsequent rows: cost matrix (diagonal 0 or empty; asymmetric allowed).
- **Graph Model**: Use `AsymmetricGraph` for cost queries; supports int/str indices/labels.
- **Testing**: Add unit tests for new features; use pytest fixtures for graphs/tours.
- **CLI Extensions**: Modify argument parser in `__init__.py` for new flags; update README examples.
- **Performance**: For large instances, use 2-opt with timeouts; benchmark with `--benchmark`.
- **Common Issues**: Ensure tour permutations are valid; handle wrap-around in cost calculations.