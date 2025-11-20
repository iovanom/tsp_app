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
- `--two-opt`: Apply 2-opt improvement to the tour after the constructive algorithm.
- `--two-opt-max-passes N`: Max improvement passes for 2-opt when no timeout is set (default: 100).
- `--two-opt-timeout S`: Timeout in seconds for 2-opt; ignores max_passes when set (default: no limit).
- `--three-opt`: Apply 3-opt improvement to the tour after the constructive algorithm.
- `--three-opt-max-passes N`: Max improvement passes for 3-opt when no timeout is set (default: 100).
- `--three-opt-timeout S`: Timeout in seconds for 3-opt; ignores max_passes when set (default: no limit).
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

Solve using nearest neighbor and apply 2-opt improvement:

```bash
uv run tsp samples/minimal_sample.csv --two-opt
```

Solve using cheapest insertion and apply 2-opt improvement:

```bash
uv run tsp samples/minimal_sample.csv --algorithm cheapest_insertion --two-opt
```

Solve with 2-opt limited to 10 passes and 1 second timeout:

```bash
uv run tsp samples/large_sample.csv --two-opt --two-opt-max-passes 10 --two-opt-timeout 1.0
```

Solve using nearest neighbor and apply 3-opt improvement:

```bash
uv run tsp samples/minimal_sample.csv --three-opt
```

Solve using cheapest insertion and apply both 2-opt and 3-opt improvement:

```bash
uv run tsp samples/minimal_sample.csv --algorithm cheapest_insertion --two-opt --three-opt
```

Solve with 3-opt limited to 50 passes and 2 second timeout:

```bash
uv run tsp samples/large_sample.csv --three-opt --three-opt-max-passes 50 --three-opt-timeout 2.0
```

Benchmark nearest neighbor with 5 runs:

```bash
uv run tsp samples/large_sample.csv --benchmark --runs 5
```

Output:
```
Algorithm: nearest_neighbor
Runs: 5
Cost - Min: 560.00, Max: 560.00, Avg: 560.00
Time - Min: 0.0017s, Max: 0.0033s, Avg: 0.0026s
```

Benchmark with 3-opt:

```bash
uv run tsp samples/large_sample.csv --three-opt --benchmark --runs 5
```

Output:
```
Algorithm: nearest_neighbor + 3-opt
Runs: 5
Cost - Min: 540.00, Max: 550.00, Avg: 545.00
Time - Min: 0.0500s, Max: 0.0800s, Avg: 0.0650s
```

## Samples

Example CSV files:

- `sample.csv` (in root): A 25-node example with labels A-Y and random costs.
- `samples/minimal_sample.csv`: A small 3-node example with labels A, B, C.
- `samples/large_sample.csv`: A 100-node example with labels A1-J10 and random costs.

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
