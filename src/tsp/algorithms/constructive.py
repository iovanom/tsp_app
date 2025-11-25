import time

from tsp.models.graph import AsymmetricGraph


def _tour_cost(graph: AsymmetricGraph, tour: list[int]) -> float:
    n = len(tour)
    return sum(graph.c(tour[i], tour[(i + 1) % n]) for i in range(n))


def nearest_neighbor(graph: AsymmetricGraph, start: int = 0) -> tuple[list[int], float]:
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


def cheapest_insertion(graph: AsymmetricGraph, start: int = 0) -> tuple[list[int], float]:
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


def two_opt(
    graph: AsymmetricGraph, tour: list[int], max_passes: int = 100, timeout: float | None = None
) -> tuple[list[int], float]:
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
    while (
        improved
        and (timeout is None or time.time() - start_time < timeout)
        and (timeout is not None or passes < max_passes)
    ):
        passes += 1
        improved = False
        for i in range(n - 2):
            for j in range(i + 2, n - 1):
                # check if swapping edges improves
                a = tour[i]
                b = tour[i + 1]
                c = tour[j]
                d = tour[j + 1]
                # cost of original middle segment b to c
                cost_original = sum(graph.c(tour[k], tour[k + 1]) for k in range(i + 1, j))
                # cost of reversed middle segment b to c
                cost_middle_new = sum(graph.c(tour[k], tour[k - 1]) for k in range(j, i + 1, -1))
                # delta = new end edges + new middle - old end edges - old middle
                delta = graph.c(a, c) + graph.c(b, d) + cost_middle_new - graph.c(a, b) - graph.c(c, d) - cost_original
                if delta < 0:
                    # reverse the segment from i+1 to j
                    tour[i + 1:j + 1] = reversed(tour[i + 1:j + 1])
                    improved = True
                    break
            if improved:
                break

    return tour, _tour_cost(graph, tour)


def three_opt(
    graph: AsymmetricGraph, tour: list[int], max_passes: int = 100, timeout: float | None = None
) -> tuple[list[int], float]:
    """
    Improves a tour using the 3-opt algorithm
    returns a tuple (tour, cost)
    max_passes: maximum number of improvement passes to prevent infinite loops
    timeout: maximum time in seconds to run (None for no limit)
    """
    n = len(tour)
    if n < 6:
        return tour, _tour_cost(graph, tour)

    improved = True
    passes = 0
    start_time = time.time()
    while (
        improved and (timeout is None or time.time() - start_time < timeout) and passes < max_passes
    ):
        passes += 1
        improved = False
        for i in range(n - 3):
            for j in range(i + 2, n - 1):
                for k in range(j + 2, n):
                    a = tour[i]
                    b = tour[i + 1]
                    c = tour[j]
                    d = tour[j + 1]
                    e = tour[k]
                    f = tour[(k + 1) % n]
                    current = graph.c(a, b) + graph.c(c, d) + graph.c(e, f)
                    cost_original1 = sum(graph.c(tour[k], tour[k + 1]) for k in range(i + 1, j))
                    cost_middle_new1 = sum(graph.c(tour[k], tour[k - 1]) for k in range(j, i + 1, -1))

                    # case 1: reverse i+1 to j
                    delta1 = graph.c(a, c) + graph.c(b, d) + cost_middle_new1 - graph.c(a, b) - graph.c(b, c) - graph.c(c, d) - cost_original1
                    if delta1 < 0:
                        old_cost = _tour_cost(graph, tour)
                        tour[i + 1:j + 1] = reversed(tour[i + 1:j + 1])
                        new_cost = _tour_cost(graph, tour)
                        if new_cost < old_cost:
                            improved = True
                            break
                        else:
                            tour[i + 1:j + 1] = reversed(tour[i + 1:j + 1])  # revert

                    # case 2: reverse j+1 to k
                    cost_original2 = sum(graph.c(tour[k], tour[k + 1]) for k in range(j + 1, k))
                    cost_middle_new2 = sum(graph.c(tour[k], tour[k - 1]) for k in range(k, j + 1, -1))
                    delta2 = graph.c(c, e) + graph.c(e, d) + graph.c(d, f) + cost_middle_new2 - graph.c(c, d) - graph.c(d, e) - graph.c(e, f) - cost_original2
                    if delta2 < 0:
                        old_cost = _tour_cost(graph, tour)
                        tour[j + 1:k + 1] = reversed(tour[j + 1:k + 1])
                        new_cost = _tour_cost(graph, tour)
                        if new_cost < old_cost:
                            improved = True
                            break
                        else:
                            tour[j + 1:k + 1] = reversed(tour[j + 1:k + 1])  # revert

                    # case 3: reverse i+1 to k
                    cost_original3 = sum(graph.c(tour[k], tour[k + 1]) for k in range(i + 1, k))
                    cost_middle_new3 = sum(graph.c(tour[k], tour[k - 1]) for k in range(k, i + 1, -1))
                    delta3 = graph.c(a, e) + graph.c(e, b) + graph.c(b, f) + cost_middle_new3 - graph.c(a, b) - graph.c(b, e) - graph.c(e, f) - cost_original3
                    if delta3 < 0:
                        old_cost = _tour_cost(graph, tour)
                        tour[i + 1:k + 1] = reversed(tour[i + 1:k + 1])
                        new_cost = _tour_cost(graph, tour)
                        if new_cost < old_cost:
                            improved = True
                            break
                        else:
                            tour[i + 1:k + 1] = reversed(tour[i + 1:k + 1])  # revert

                    # case 4: reverse i+1 to j and j+1 to k
                    cost_original4a = sum(graph.c(tour[k], tour[k + 1]) for k in range(i + 1, j))
                    cost_middle_new4a = sum(graph.c(tour[k], tour[k - 1]) for k in range(j, i + 1, -1))
                    cost_original4b = sum(graph.c(tour[k], tour[k + 1]) for k in range(j + 1, k))
                    cost_middle_new4b = sum(graph.c(tour[k], tour[k - 1]) for k in range(k, j + 1, -1))
                    delta4 = graph.c(a, c) + graph.c(c, b) + graph.c(c, e) + graph.c(e, d) + graph.c(d, f) + cost_middle_new4a + cost_middle_new4b - graph.c(a, b) - graph.c(b, c) - graph.c(c, d) - graph.c(d, e) - graph.c(e, f) - cost_original4a - cost_original4b
                    if delta4 < 0:
                        old_cost = _tour_cost(graph, tour)
                        tour[i + 1:j + 1] = reversed(tour[i + 1:j + 1])
                        tour[j + 1:k + 1] = reversed(tour[j + 1:k + 1])
                        new_cost = _tour_cost(graph, tour)
                        if new_cost < old_cost:
                            improved = True
                            break
                        else:
                            tour[i + 1:j + 1] = reversed(tour[i + 1:j + 1])  # revert
                            tour[j + 1:k + 1] = reversed(tour[j + 1:k + 1])  # revert

                if improved:
                    break
            if improved:
                break

    return tour, _tour_cost(graph, tour)
