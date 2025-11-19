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
