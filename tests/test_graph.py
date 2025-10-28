import math
import pytest

from tsp.models.graph import AsymmetricGraph


def test_construct_minimal_and_defaults():
    g = AsymmetricGraph([[math.inf, 1], [2, math.inf]])
    assert g.n == 2
    assert g.labels == ["0", "1"]
    assert g.c(0, 1) == 1.0
    assert g.c(1, 0) == 2.0
    assert math.isinf(g.c(0, 0)) and math.isinf(g.c(1, 1))


def test_construct_with_labels():
    g = AsymmetricGraph([[None, "3.5"], ["", None]], labels=["A", "B"])
    assert g.labels == ["A", "B"]
    assert g.n == 2
    assert g.c(0, 1) == 3.5
    assert math.isinf(g.c(1, 0))


def test_invalid_non_square_matrix():
    with pytest.raises(ValueError):
        AsymmetricGraph([[math.inf, 1, 2], [3, math.inf, 4]])


def test_invalid_value_non_numeric():
    with pytest.raises(ValueError):
        AsymmetricGraph([[math.inf, "abc"], [1, math.inf]])


def test_invalid_labels_length():
    with pytest.raises(ValueError):
        AsymmetricGraph([[math.inf, 1], [2, math.inf]], labels=["A"])


def test_index_out_of_bounds():
    g = AsymmetricGraph([[math.inf, 1], [2, math.inf]])
    with pytest.raises(IndexError):
        g.c(-1, 0)
    with pytest.raises(IndexError):
        g.c(0, 2)
