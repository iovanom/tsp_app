from tsp.models.graph import AsymmetricGraph
from tsp.algorithms.constructive import nearest_neighbor, three_opt


def _tour_cost(g: AsymmetricGraph, tour: list[int]) -> float:
    n = len(tour)
    return sum(g.c(tour[i], tour[(i + 1) % n]) for i in range(n))


def test_three_opt_improves_tour():
    # Create a graph where we can test improvement
    m = [
        [float('inf'), 1, 10, 5, 8],
        [5, float('inf'), 1, 10, 3],
        [10, 5, float('inf'), 1, 7],
        [1, 10, 5, float('inf'), 2],
        [8, 3, 7, 2, float('inf')],
    ]
    g = AsymmetricGraph(m)
    # Nearest neighbor from 0: 0->1 (1), 1->2 (1), 2->3 (1), 3->4 (2), total ~5
    tour, cost = nearest_neighbor(g, 0)
    initial_cost = cost
    improved_tour, improved_cost = three_opt(g, tour.copy())
    assert improved_cost <= initial_cost
    assert len(improved_tour) == 5
    assert set(improved_tour) == set(range(5))


def test_three_opt_no_improvement():
    # Use a graph where nearest neighbor gives optimal
    m = [
        [float('inf'), 1, 10, 5],
        [5, float('inf'), 1, 10],
        [10, 5, float('inf'), 1],
        [1, 10, 5, float('inf')],
    ]
    g = AsymmetricGraph(m)
    optimal_tour = [0, 1, 2, 3]
    tour, cost = three_opt(g, optimal_tour.copy())
    assert tour == optimal_tour
    assert cost == 4.0


def test_three_opt_small_graph():
    # 5 nodes, should work
    m = [
        [float('inf'), 1, 2, 3, 4],
        [4, float('inf'), 1, 2, 3],
        [3, 4, float('inf'), 1, 2],
        [2, 3, 4, float('inf'), 1],
        [1, 2, 3, 4, float('inf')],
    ]
    g = AsymmetricGraph(m)
    initial_tour = [0, 1, 2, 3, 4]
    tour, cost = three_opt(g, initial_tour.copy())
    assert len(tour) == 5
    assert set(tour) == {0, 1, 2, 3, 4}
    assert cost == _tour_cost(g, tour)