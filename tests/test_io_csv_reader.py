import pytest
import tempfile
import os
from tsp.io.csv_reader import _read_csv_matrix_file, _create_asymmetric_matrix
from tsp.models.graph import AsymmetricGraph


class TestReadCsvMatrixFile:
    """Tests for _read_csv_matrix_file"""

    def test_read_with_header(self):
        """Test reading CSV with header"""
        content = "A,B,C\n1,2,3\n4,5,6\n7,8,9"
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            f.write(content)
            temp_path = f.name

        try:
            rows, header = _read_csv_matrix_file(temp_path, has_header=True)
            assert header == ['A', 'B', 'C']
            assert rows == [['1', '2', '3'], ['4', '5', '6'], ['7', '8', '9']]
        finally:
            os.unlink(temp_path)

    def test_read_without_header(self):
        """Test reading CSV without header"""
        content = "1,2,3\n4,5,6\n7,8,9"
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            f.write(content)
            temp_path = f.name
        try:
            rows, header = _read_csv_matrix_file(temp_path, has_header=False)
            assert header is None
            assert rows == [['1', '2', '3'], ['4', '5', '6'], ['7', '8', '9']]
        finally:
            os.unlink(temp_path)

    def test_read_with_custom_delimiter(self):
        """Test reading CSV with custom delimiter"""
        content = "A;B;C\n1;2;3\n4;5;6"
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            f.write(content)
            temp_path = f.name
        try:
            rows, header = _read_csv_matrix_file(temp_path, has_header=True, delimiter=';')
            assert header == ['A', 'B', 'C']
            assert rows == [['1', '2', '3'], ['4', '5', '6']]
        finally:
            os.unlink(temp_path)

    def test_read_empty_file(self):
        """Test reading empty file"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            f.write("")
            temp_path = f.name
        try:
            with pytest.raises(ValueError, match="empty CSV"):
                _read_csv_matrix_file(temp_path)
        finally:
            os.unlink(temp_path)

    def test_read_with_empty_lines(self):
        """Test reading CSV with empty lines (should be ignored)"""
        content = "A,B,C\n1,2,3\n\n4,5,6\n  \n7,8,9"
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            f.write(content)
            temp_path = f.name
        try:
            rows, header = _read_csv_matrix_file(temp_path, has_header=True)
            assert header == ['A', 'B', 'C']
            assert len(rows) == 3
            assert rows == [['1', '2', '3'], ['4', '5', '6'], ['7', '8', '9']]
        finally:
            os.unlink(temp_path)

    def test_read_with_whitespace(self):
        """Test reading CSV with whitespace"""
        content = " A , B , C \n 1 , 2 , 3 \n 4 , 5 , 6 "
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            f.write(content)
            temp_path = f.name
        try:
            rows, header = _read_csv_matrix_file(temp_path, has_header=True)
            # Values are not trimmed automatically by csv.reader
            assert header == [' A ', ' B ', ' C ']
            assert rows == [[' 1 ', ' 2 ', ' 3 '], [' 4 ', ' 5 ', ' 6 ']]
        finally:
            os.unlink(temp_path)


class TestCreateAsymmetricMatrix:
    """Tests for _create_asymmetric_matrix"""

    def test_create_without_header(self):
        """Test creating matrix without header"""
        rows = [['0', '10', '15'], ['12', '0', '20'], ['8', '18', '0']]
        graph = _create_asymmetric_matrix(rows, header=None)
        assert isinstance(graph, AsymmetricGraph)
        assert graph.labels == ['0', '1', '2']

    def test_create_with_header_no_first_col(self):
        """Test creating matrix with header, without label column"""
        rows = [['0', '10', '15'], ['12', '0', '20'], ['8', '18', '0']]
        header = ['A', 'B', 'C']
        graph = _create_asymmetric_matrix(rows, header)
        assert isinstance(graph, AsymmetricGraph)
        assert graph.labels == ['A', 'B', 'C']

    def test_create_with_header_and_first_col_empty(self):
        """Test creating matrix with header and first cell empty"""
        rows = [['A', '0', '10', '15'], ['B', '12', '0', '20'], ['C', '8', '18', '0']]
        header = ['', 'A', 'B', 'C']
        graph = _create_asymmetric_matrix(rows, header)
        assert isinstance(graph, AsymmetricGraph)
        assert graph.labels == ['A', 'B', 'C']

    def test_create_with_header_and_first_col_dash(self):
        """Test creating matrix with header and first cell '-'"""
        rows = [['A', '0', '10'], ['B', '12', '0']]
        header = ['-', 'A', 'B']
        graph = _create_asymmetric_matrix(rows, header)
        assert isinstance(graph, AsymmetricGraph)
        assert graph.labels == ['A', 'B']

    def test_create_matrix_too_small(self):
        """Test creating matrix too small (< 2 rows)"""
        rows = [['0', '10']]
        with pytest.raises(ValueError, match="matrix must have at least two rows"):
            _create_asymmetric_matrix(rows)

    def test_create_header_too_small(self):
        """Test header too small"""
        rows = [['0', '10'], ['12', '0']]
        header = ['A']
        with pytest.raises(ValueError, match="header must have at least two cells"):
            _create_asymmetric_matrix(rows, header)

    def test_create_header_size_mismatch(self):
        """Test mismatch between header size and number of rows"""
        rows = [['0', '10'], ['12', '0']]
        header = ['A', 'B', 'C']
        with pytest.raises(ValueError, match="header must have the same number of cells"):
            _create_asymmetric_matrix(rows, header)

    def test_create_rows_inconsistent_length(self):
        """Test rows with different lengths"""
        rows = [['0', '10', '15'], ['12', '0']]
        with pytest.raises(ValueError, match="each row must have the same number of cells"):
            _create_asymmetric_matrix(rows)

    def test_create_with_whitespace_in_labels(self):
        """Test labels with spaces (should be trimmed)"""
        rows = [['0', '10'], ['12', '0']]
        header = [' A ', ' B ']
        graph = _create_asymmetric_matrix(rows, header)
        assert graph.labels == ['A', 'B']

    def test_create_valid_asymmetric_matrix(self):
        """Test creating valid asymmetric matrix"""
        rows = [['0', '10', '15'], ['5', '0', '20'], ['8', '18', '0']]
        header = ['A', 'B', 'C']
        graph = _create_asymmetric_matrix(rows, header)
        assert isinstance(graph, AsymmetricGraph)
        assert graph.labels == ['A', 'B', 'C']
