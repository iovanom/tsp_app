import time
from typing import Optional

from tsp.models.graph import AsymmetricGraph


def _tour_cost(graph: AsymmetricGraph, tour: list[int]) -> float:
    n = len(tour)
    return sum(graph.c(tour[i], tour[(i + 1) % n]) for i in range(n))


def nearest_neighbor(
    graph: AsymmetricGraph, start: int = 0
) -> tuple[list[int], float]:
    """
    Constructs a tour using the nearest neighbor algorithm
    returns a tuple (tour, cost)
    """
    n = graph.n
    if not (0 <= start < n):
        raise IndexError("start must be a valid node index")

    visited = [False] * n
    tour: list[int] = [start]
    visited[start] = True
    current = start

    while len(tour) < n:
        # choose nearest unvisited (deterministic tie-break by index)
        next_city = min(
            (j for j in range(n) if not visited[j]),
            key=lambda j: (graph.c(current, j), j),
        )
        tour.append(next_city)
        visited[next_city] = True
        current = next_city

    return tour, _tour_cost(graph, tour)


def cheapest_insertion(
    graph: AsymmetricGraph, start: int = 0
) -> tuple[list[int], float]:
    """
    Constructs a tour using the cheapest insertion algorithm
    returns a tuple (tour, cost)
    """
    n = graph.n
    if not (0 <= start < n):
        raise IndexError("start must be a valid node index")

    if n == 1:
        return [start], 0.0

    # start with a 2-node cycle: start -> nearest -> start
    nearest = min(
        (j for j in range(n) if j != start),
        key=lambda j: (graph.c(start, j), j),
    )
    cycle: list[int] = [start, nearest]

    remaining = {j for j in range(n) if j not in cycle}

    while remaining:
        best_k = None
        best_pos = None
        best_delta = None

        m = len(cycle)
        # consider all edges including wrap-around (last -> first)
        for k in remaining:
            for i in range(m):
                a = cycle[i]
                b = cycle[(i + 1) % m]
                delta = graph.c(a, k) + graph.c(k, b) - graph.c(a, b)
                key = (delta, k, i)
                if best_delta is None or key < (best_delta, best_k, best_pos):
                    best_delta = delta
                    best_k = k
                    best_pos = i + 1  # insert after position i

        # insert the selected node at the best position
        cycle.insert(best_pos, best_k)  # type: ignore[arg-type]
        remaining.remove(best_k)  # type: ignore[arg-type]

    # ensure representation starts at 'start'
    if cycle[0] != start:
        idx = cycle.index(start)
        cycle = cycle[idx:] + cycle[:idx]

    return cycle, _tour_cost(graph, cycle)


def two_opt(graph: AsymmetricGraph, tour: list[int], max_passes: int = 100, timeout: float | None = None) -> tuple[list[int], float]:
    """
    Improves a tour using the 2-opt algorithm
    returns a tuple (tour, cost)
    max_passes: maximum number of improvement passes to prevent infinite loops
    timeout: maximum time in seconds to run (None for no limit)
    """
    n = len(tour)
    if n < 4:
        return tour, _tour_cost(graph, tour)

    improved = True
    passes = 0
    start_time = time.time()
    while improved and (timeout is None or time.time() - start_time < timeout) and (timeout is not None or passes < max_passes):
        passes += 1
        improved = False
        for i in range(n - 2):
            for j in range(i + 2, n - 1):
                # check if swapping edges improves
                a = tour[i]
                b = tour[i + 1]
                c = tour[j]
                d = tour[j + 1]
                # current cost: a->b + c->d
                # new cost: a->c + b->d
                delta = graph.c(a, c) + graph.c(b, d) - graph.c(a, b) - graph.c(c, d)
                if delta < 0:
                    # reverse the segment from i+1 to j
                    tour[i + 1 : j + 1] = reversed(tour[i + 1 : j + 1])
                    improved = True
                    break
            if improved:
                break

    return tour, _tour_cost(graph, tour)
