from pathlib import Path
import duckdb
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DB_FILE = BASE_DIR / "lab8.duckdb"
print("DB_FILE inside module =", DB_FILE)


def get_latest_data(csv_file: str) -> pd.DataFrame:
    df = pd.read_csv(csv_file)

    date_col = df.columns[0]
    value_col = df.columns[1]

    result = df[[date_col, value_col]].copy()
    result.columns = ["date", "cpi"]

    result["cpi"] = pd.to_numeric(result["cpi"], errors="coerce")
    result = result.dropna(subset=["cpi"])

    return result


def create_append_table(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS cpi_append (
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


def load_append(csv_file: str, init: bool = False):
    df = get_latest_data(csv_file)

    conn = duckdb.connect(DB_FILE)
    create_append_table(conn)

    if init:
        conn.execute("DELETE FROM cpi_append")

    conn.register("incoming_df", df)

    conn.execute("""
        INSERT INTO cpi_append
        SELECT i.date, i.cpi
        FROM incoming_df i
        WHERE NOT EXISTS (
            SELECT 1
            FROM cpi_append t
            WHERE t.date = i.date AND t.cpi = i.cpi
        )
    """)

    conn.close()


def load_trunc(csv_file: str):
    df = get_latest_data(csv_file)

    conn = duckdb.connect(DB_FILE)
    create_trunc_table(conn)

    conn.execute("DELETE FROM cpi_trunc")
    conn.register("incoming_df", df)

    conn.execute("""
        INSERT INTO cpi_trunc
        SELECT date, cpi
        FROM incoming_df
    """)

    conn.close()


def load_incremental(csv_file: str, init: bool = False):
    df = get_latest_data(csv_file)

    conn = duckdb.connect(DB_FILE)
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


def show_table(table_name: str):
    conn = duckdb.connect(DB_FILE)
    df = conn.execute(f"SELECT * FROM {table_name} ORDER BY date").df()
    conn.close()
    return df
