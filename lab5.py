import pandas as pd
import numpy as np
from test_helper import parse_dollars


def load_hw4():
    return pd.read_csv("HW4_1.csv")



def test_no_missing_in_key_columns():
    df = load_hw4()
    key_cols = ["fare", "passen", "dist", "bmktshr", "fare_str"]
    assert df[key_cols].isna().sum().sum() == 0



def test_bmktshr_range():
    df = load_hw4()
    assert (df["bmktshr"] >= 0).all()
    assert (df["bmktshr"] <= 1).all()


# 3️⃣ 票价和距离必须为正数def test_positive_values():
    df = load_hw4()
    assert (df["fare"] > 0).all()
    assert (df["dist"] > 0).all()
    assert (df["passen"] > 0).all()


# 4️⃣ log 列必须等于原列的 logdef test_log_columns_consistency():
    df = load_hw4()

    assert np.allclose(df["lfare"], np.log(df["fare"]), atol=1e-6)
    assert np.allclose(df["lpassen"], np.log(df["passen"]), atol=1e-6)
    assert np.allclose(df["ldist"], np.log(df["dist"]), atol=1e-6)
    assert np.allclose(df["lbmktshr"], np.log(df["bmktshr"]), atol=1e-6)



def test_fare_str_matches_fare():
    df = load_hw4()
    parsed = parse_dollars(df["fare_str"])

    assert np.allclose(parsed, df["fare"], atol=0.01)