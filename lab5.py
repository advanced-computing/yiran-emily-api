import pandas as pd
import numpy as np
from test_helper import parse_dollars

def load_hw4():
    return pd.read_csv("HW4_1.csv")

def test_key_columns_not_missing():
    df = load_hw4()
    key_cols = ["fare", "passen", "dist", "bmktshr", "fare_str"]
    assert df[key_cols].isna().sum().sum() == 0

def test_bmktshr_range():
    df = load_hw4()
    assert (df["bmktshr"] >= 0).all()
    assert (df["bmktshr"] <= 1).all()

def test_fare_str_matches_fare():
    df = load_hw4()
    parsed = parse_dollars(df["fare_str"])
    assert np.allclose(parsed.to_numpy(), df["fare"].astype(float).to_numpy(), atol=0.01)