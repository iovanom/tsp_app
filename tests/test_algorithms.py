from typing import List
import math
import pytest

from tsp.models.graph import AsymmetricGraph
from tsp.algorithms.constructive import (
    nearest_neighbor,
    cheapest_insertion,
)


def _build_graph() -> AsymmetricGraph:
    # Deterministic 4-node instance; unique nearest choices
    m: List[List[float]] = [
        [math.inf, 1, 5, 10],
        [5, math.inf, 1, 10],
        [10, 5, math.inf, 1],
        [1, 10, 5, math.inf],
    ]
    return AsymmetricGraph(m)


def _tour_cost(g: AsymmetricGraph, tour: list[int]) -> float:
    n = len(tour)
    return sum(g.c(tour[i], tour[(i + 1) % n]) for i in range(n))


def _assert_valid_tour(g: AsymmetricGraph, tour: list[int], start: int) -> None:
    assert len(tour) == g.n
    assert len(set(tour)) == g.n
    assert tour[0] == start


def test_nearest_neighbor_default_start():
    g = _build_graph()
    tour, cost = nearest_neighbor(g)
    _assert_valid_tour(g, tour, start=0)
    assert tour == [0, 1, 2, 3]
    assert cost == pytest.approx(4.0)
    assert cost == pytest.approx(_tour_cost(g, tour))


def test_nearest_neighbor_custom_start():
    g = _build_graph()
    tour, cost = nearest_neighbor(g, start=2)
    _assert_valid_tour(g, tour, start=2)
    assert tour == [2, 3, 0, 1]
    assert cost == pytest.approx(4.0)
    assert cost == pytest.approx(_tour_cost(g, tour))


def test_cheapest_insertion_default_start():
    g = _build_graph()
    tour, cost = cheapest_insertion(g)
    _assert_valid_tour(g, tour, start=0)
    # Sequence may vary; cost should match the cycle cost
    assert cost == pytest.approx(4.0)
    assert cost == pytest.approx(_tour_cost(g, tour))


def test_cheapest_insertion_custom_start():
    g = _build_graph()
    tour, cost = cheapest_insertion(g, start=2)
    _assert_valid_tour(g, tour, start=2)
    assert cost == pytest.approx(4.0)
    assert cost == pytest.approx(_tour_cost(g, tour))
