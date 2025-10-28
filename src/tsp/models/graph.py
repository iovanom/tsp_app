from typing import List
import math

type Label = str | int


class AsymmetricGraph:
    def __init__(self, cost_matrix: List[List[float]], labels: List[str] = None):
        if not cost_matrix:
            raise ValueError("cost_matrix cannot be empty")
        if any(not isinstance(row, list) for row in cost_matrix):
            raise ValueError("cost_matrix must be a list of lists")
        n = len(cost_matrix)
        if any(len(row) != n for row in cost_matrix):
            raise ValueError("cost_matrix must be a square matrix")

        norm = []
        for i, row in enumerate(cost_matrix):
            new_row = []
            for j, val in enumerate(row):
                # diagonal is set to infinity
                if i == j:
                    new_row.append(math.inf)
                    continue
                try:
                    if val is None or (isinstance(val, str) and val.strip() in ["", "inf"]):
                        new_row.append(math.inf)
                    else:
                        new_row.append(float(val))
                except ValueError:
                    raise ValueError(f"cost_matrix[{i}][{j}] = {val} must be a number")
            norm.append(new_row)

        self._cost = norm
        self._n = n

        if labels is not None:
            if len(set(labels)) != n:
                raise ValueError("len(labels) must be equal to n and labels must be unique")
            self._labels = list(map(str, labels))
        else:
            self._labels = list(map(str, range(n)))

        self._labels_map = {label: i for i, label in enumerate(self._labels)}

    @property
    def n(self) -> int:
        return self._n

    @property
    def labels(self) -> List[str]:
        return self._labels

    def c(self, i: Label, j: Label) -> float:
        try:
            if isinstance(i, str):
                i = self._labels_map[i]
            if isinstance(j, str):
                j = self._labels_map[j]
        except KeyError:
            raise ValueError(f"{i} or {j} is not in labels")

        if not (0 <= i <= self._n and 0 <= j <= self._n):
            raise IndexError(f"i and j must be between 0 and {self._n}")
        return self._cost[i][j]
