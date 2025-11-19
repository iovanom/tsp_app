from tsp.models.graph import AsymmetricGraph
from tsp.algorithms.constructive import nearest_neighbor, two_opt


def _tour_cost(g: AsymmetricGraph, tour: list[int]) -> float:
    n = len(tour)
    return sum(g.c(tour[i], tour[(i + 1) % n]) for i in range(n))


def test_two_opt_improves_tour():
    # Create a graph where we can test improvement
    m = [
        [float('inf'), 1, 10, 5],
        [5, float('inf'), 1, 10],
        [10, 5, float('inf'), 1],
        [1, 10, 5, float('inf')],
    ]
    g = AsymmetricGraph(m)
    # Nearest neighbor from 0: 0->1 (1), then 1->2 (1), then 2->3 (1), total 4
    tour, cost = nearest_neighbor(g, 0)
    assert tour == [0, 1, 2, 3]
    assert cost == 4.0  # already optimal

    # To test improvement, create a worse initial tour
    initial_tour = [0, 3, 2, 1]  # cost: 0->3:5, 3->2:5, 2->1:5, 1->0:5 = 20
    improved_tour, improved_cost = two_opt(g, initial_tour.copy())
    assert improved_cost <= _tour_cost(g, initial_tour)
    assert len(improved_tour) == 4
    assert set(improved_tour) == set(range(4))


def test_two_opt_no_improvement():
    # Use the same graph, start with optimal tour
    m = [
        [float('inf'), 1, 10, 5],
        [5, float('inf'), 1, 10],
        [10, 5, float('inf'), 1],
        [1, 10, 5, float('inf')],
    ]
    g = AsymmetricGraph(m)
    optimal_tour = [0, 1, 2, 3]
    tour, cost = two_opt(g, optimal_tour.copy())
    assert tour == optimal_tour
    assert cost == 4.0


def test_two_opt_small_graph():
    # 3 nodes, 2-opt shouldn't change much
    m = [
        [float('inf'), 1, 2],
        [3, float('inf'), 1],
        [2, 4, float('inf')],
    ]
    g = AsymmetricGraph(m)
    initial_tour = [0, 1, 2]
    tour, cost = two_opt(g, initial_tour.copy())
    assert len(tour) == 3
    assert set(tour) == {0, 1, 2}
    assert cost == _tour_cost(g, tour)
