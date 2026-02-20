import pandas as pd

def parse_dollars(amounts: pd.Series):
    dollar_str = amounts.str.replace("$", '', regex=False).str.replace(',' , '').astype(float)
    return dollar_str.astype(float)