from pathlib import Path
import re
import duckdb
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DB_FILE = BASE_DIR / "lab8_full.duckdb"
SOURCE_FILE = BASE_DIR / "data" / "pcpi_vintages.csv"


def vintage_to_date(vintage_col: str) -> pd.Timestamp:
    """
    Convert a vintage column like PCPI04M1 to a release date.
    Example:
        PCPI04M1 -> 2004-01-01
        PCPI25M2 -> 2025-02-01
    """
    match = re.match(r"PCPI(\d{2})M(\d{1,2})$", vintage_col)
    if not match:
        raise ValueError(f"Invalid vintage column: {vintage_col}")

    yy = int(match.group(1))
    mm = int(match.group(2))
    year = 2000 + yy
    return pd.Timestamp(year=year, month=mm, day=1)


def get_latest_vintage_name(pull_date: str, csv_file: str | Path = SOURCE_FILE) -> str | None:
    df = pd.read_csv(csv_file, nrows=1)
    pull_date = pd.to_datetime(pull_date)

    vintage_cols = [col for col in df.columns if re.match(r"PCPI\d{2}M\d{1,2}$", col)]
    available_cols = [col for col in vintage_cols if vintage_to_date(col) <= pull_date]

    if not available_cols:
        return None

    return max(available_cols, key=vintage_to_date)


def get_latest_data(pull_date: str, csv_file: str | Path = SOURCE_FILE) -> pd.DataFrame:
    df = pd.read_csv(csv_file)
    pull_date = pd.to_datetime(pull_date)

    date_col = df.columns[0]
    vintage_cols = [col for col in df.columns if re.match(r"PCPI\d{2}M\d{1,2}$", col)]

    available_cols = [col for col in vintage_cols if vintage_to_date(col) <= pull_date]

    if not available_cols:
        return pd.DataFrame(columns=["date", "cpi"])

    latest_col = max(available_cols, key=vintage_to_date)

    result = df[[date_col, latest_col]].copy()
    result.columns = ["date", "cpi"]
    result["cpi"] = pd.to_numeric(result["cpi"], errors="coerce")
    result = result.dropna(subset=["cpi"])

    return result


def create_append_table(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS cpi_append (
            pull_date DATE,
            date VARCHAR,
            cpi DOUBLE
        )
    """)


def create_trunc_table(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS cpi_trunc (
            date VARCHAR,
            cpi DOUBLE
        )
    """)


def create_inc_table(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS cpi_inc (
            date VARCHAR PRIMARY KEY,
            cpi DOUBLE
        )
    """)


def load_append(pull_date: str, init: bool = False):
    df = get_latest_data(pull_date)
    df["pull_date"] = pd.to_datetime(pull_date).date()
    df = df[["pull_date", "date", "cpi"]]

    conn = duckdb.connect(str(DB_FILE))
    create_append_table(conn)

    if init:
        conn.execute("DELETE FROM cpi_append")

    conn.register("incoming_df", df)
    conn.execute("""
        INSERT INTO cpi_append
        SELECT pull_date, date, cpi
        FROM incoming_df
    """)
    conn.close()


def load_trunc(pull_date: str):
    df = get_latest_data(pull_date)

    conn = duckdb.connect(str(DB_FILE))
    create_trunc_table(conn)

    conn.execute("DELETE FROM cpi_trunc")
    conn.register("incoming_df", df)
    conn.execute("""
        INSERT INTO cpi_trunc
        SELECT date, cpi
        FROM incoming_df
    """)
    conn.close()


def load_incremental(pull_date: str, init: bool = False):
    df = get_latest_data(pull_date)

    conn = duckdb.connect(str(DB_FILE))
    create_inc_table(conn)

    if init:
        conn.execute("DELETE FROM cpi_inc")

    conn.register("incoming_df", df)
    conn.execute("""
        MERGE INTO cpi_inc AS target
        USING incoming_df AS source
        ON target.date = source.date
        WHEN MATCHED AND target.cpi <> source.cpi THEN
            UPDATE SET cpi = source.cpi
        WHEN NOT MATCHED THEN
            INSERT (date, cpi)
            VALUES (source.date, source.cpi)
    """)
    conn.close()


def show_table(table_name: str) -> pd.DataFrame:
    conn = duckdb.connect(str(DB_FILE))
    df = conn.execute(f"SELECT * FROM {table_name} ORDER BY 1, 2").df()
    conn.close()
    return df