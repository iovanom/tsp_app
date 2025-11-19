# TSP Solver

<!--toc:start-->
- [TSP Solver](#tsp-solver)
  - [Installation](#installation)
  - [Usage](#usage)
    - [CLI](#cli)
      - [Options](#options)
      - [Examples](#examples)
  - [Samples](#samples)
  - [Testing](#testing)
  - [Development](#development)
<!--toc:end-->

A Python CLI tool for solving the Traveling Salesman Problem (TSP) using constructive algorithms.

## Installation

Install dependencies:

```bash
uv sync --group dev
```

## Usage

### CLI

Run the TSP solver:

```bash
uv run tsp <csv_file> [options]
```

#### Options

- `csv_file`: Path to the CSV file containing the cost matrix.
- `--start N`: Starting node index (default: 0).
- `--algorithm {nearest_neighbor,cheapest_insertion}`: Algorithm to use (default: nearest_neighbor).
- `--benchmark`: Run benchmark mode with multiple runs.
- `--runs N`: Number of runs for benchmark (default: 10).

#### Examples

Solve TSP using nearest neighbor (default):

```bash
uv run tsp samples/minimal_sample.csv
```

Output:
```
Tour: ['A', 'B', 'C']
Cost: 38.0
```

Solve using the cheapest insertion:

```bash
uv run tsp samples/minimal_sample.csv --algorithm cheapest_insertion
```

Benchmark nearest neighbor with 5 runs:

```bash
uv run tsp samples/large_sample.csv --benchmark --runs 5
```

Output:
```
Algorithm: nearest_neighbor
Runs: 5
Cost - Min: 357.00, Max: 357.00, Avg: 357.00
Time - Min: 0.0002s, Max: 0.0002s, Avg: 0.0002s
```

## Samples

The `samples/` folder contains example CSV files:

- `minimal_sample.csv`: A small 3-node example with labels A, B, C.
- `large_sample.csv`: A 25-node example with random costs.

CSV format: First row is header with node labels. Subsequent rows are the cost matrix (asymmetric, diagonal should be 0 or empty).

## Testing

Run all tests:

```bash
uv run pytest -q
```

Run specific test file:

```bash
uv run pytest tests/test_graph.py -q
```

Run specific test:

```bash
uv run pytest tests/test_graph.py::test_construct_minimal_and_defaults -q
```

Filter tests by pattern:

```bash
uv run pytest -k "pattern" -q
```

## Development

Format code:

```bash
uv run black . && uv run isort .
```

Lint (check only):

```bash
uv run black --check . && uv run isort --check-only . && uv run flake8
```

Build package:

```bash
uv build
```
