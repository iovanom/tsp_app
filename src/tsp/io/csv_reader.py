import csv
from typing import Optional

from tsp.models.graph import AsymmetricGraph


def read_asymetric_matrix(
    path: str,
    has_header: bool = True,
    delimiter: str = ","
) -> AsymmetricGraph:
    rows, header = _read_csv_matrix_file(path, has_header, delimiter)
    return _create_asymmetric_matrix(rows, header)


def _read_csv_matrix_file(
    path: str,
    has_header: bool = True,
    delimiter: str = ","
) -> tuple[list[list[str]], Optional[list[str]]]:
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=delimiter)
        rows = [row for row in reader if any(cell.strip() for cell in row)]

        if not rows:
            raise ValueError("empty CSV")

        header = None
        if has_header:
            header = rows[0]
            rows = rows[1:]

        return (rows, header)


def _create_asymmetric_matrix(
    rows: list[list[str]],
    header: Optional[list[str]] = None
) -> AsymmetricGraph:
    labels: Optional[list[str]] = None

    n = len(rows)
    if n < 2:
        raise ValueError("matrix must have at least two rows")

    if header:
        # first row is labels, the first cell can be empty
        if len(header) < 2:
            raise ValueError("header must have at least two cells")

        label_in_first_col = False
        if header[0].strip() in ["", "-"]:
            label_in_first_col = True
            header = header[1:]

        if len(header) != n:
            raise ValueError("header must have the same number of cells as the number of rows")

        labels = [h.strip() for h in header]
        if label_in_first_col:
            # TODO: sort the matrix by labels
            rows = [r[1:] for r in rows]

    if any(len(r) != n for r in rows):
        raise ValueError("each row must have the same number of cells as the header")

    return AsymmetricGraph(rows, labels)
