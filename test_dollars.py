import pandas as pd
import numpy as np
import pytest

from test_helper import parse_dollars

def test_parse_dollars_basic():
    amounts = pd.Series(["5", "5.99", "$100", "$100.00"])
    expected = pd.Series([5.00, 5.99, 100.00, 100.00])

    result = parse_dollars(amounts)

    assert np.allclose(result.to_numpy(), expected.to_numpy())
    assert result.dtype == float


def test_parse_dollars_commas_and_spaces():
    amounts = pd.Series([" $1,234.50 ", "$0", "2,000"])
    expected = pd.Series([1234.50, 0.00, 2000.00])

    result = parse_dollars(amounts)

    assert np.allclose(result.to_numpy(), expected.to_numpy())


def test_parse_dollars_returns_new_series():
    amounts = pd.Series(["$1", "$2"])
    result = parse_dollars(amounts)
    assert result is not amounts