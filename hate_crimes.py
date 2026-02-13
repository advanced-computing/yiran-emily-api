from flask import Flask, request, Response, jsonify
import pandas as pd
import re
import os

app = Flask(__name__)

DATA_FILE = os.path.join("data", "NYPD_Hate_Crimes_20260130.csv")


ID_COL = "full_complaint_id"


def normalize_col(name: str) -> str:
 
    name = name.strip().lower()
    name = re.sub(r"[^a-z0-9]+", "_", name)   # non-alnum -> _
    name = re.sub(r"_+", "_", name).strip("_")
    return name


def load_data() -> pd.DataFrame:
   
    if not os.path.exists(DATA_FILE):
        raise FileNotFoundError(
            f"CSV not found: {DATA_FILE}. Put the file in data/ and name it NYPD_Hate_Crimes_20260130.csv"
        )

    df = pd.read_csv(DATA_FILE, dtype=str)  # keep everything as strings
    df.columns = [normalize_col(c) for c in df.columns]

    if ID_COL not in df.columns:
        return df  # let endpoint handle error cleanly

    # Clean ID values (strip spaces)
    df[ID_COL] = df[ID_COL].fillna("").str.strip()
    return df


def apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
  
    for col, val in filters.items():
        if col not in df.columns:
            # Unknown column -> return empty set (or you could return error)
            return df.iloc[0:0]

        # Compare as strings (case-sensitive by default)
        df = df[df[col].fillna("").astype(str) == str(val)]
    return df


def apply_limit_offset(df: pd.DataFrame, limit: int, offset: int) -> pd.DataFrame:
    if offset < 0:
        offset = 0
    if limit < 0:
        limit = 0
    return df.iloc[offset: offset + limit]


def dataframe_to_json(df: pd.DataFrame) -> Response:
    return Response(df.to_json(orient="records"), mimetype="application/json")


def dataframe_to_csv(df: pd.DataFrame) -> Response:
    return Response(df.to_csv(index=False), mimetype="text/csv")


@app.route("/")
def home():
    return jsonify({
        "message": "NYPD Hate Crimes API",
        "endpoints": [
            "/api/records",
            f"/api/records/<{ID_COL}>"
        ],
        "id_column": ID_COL,
        "tip": "Use format=json or format=csv. Any other query params act as filters."
    })


@app.get("/api/records")
def list_records():

    df = load_data()

    if ID_COL not in df.columns:
        return jsonify({
            "error": f"Expected ID column '{ID_COL}' not found after normalization.",
            "found_columns_sample": df.columns.tolist()[:15]
        }), 500

    fmt = request.args.get("format", "json").lower()
    limit = request.args.get("limit", default=1000, type=int)
    offset = request.args.get("offset", default=0, type=int)

    reserved = {"limit", "offset", "format"}
    filters = {k: v for k, v in request.args.items() if k not in reserved}

    df = apply_filters(df, filters)
    df = apply_limit_offset(df, limit, offset)

    if fmt == "json":
        return dataframe_to_json(df)
    elif fmt == "csv":
        return dataframe_to_csv(df)
    else:
        return jsonify({"error": "Invalid format. Use format=json or format=csv"}), 400


@app.get(f"/api/records/<record_id>")
def get_record(record_id):
 
    df = load_data()

    if ID_COL not in df.columns:
        return jsonify({
            "error": f"Expected ID column '{ID_COL}' not found after normalization."
        }), 500

    fmt = request.args.get("format", "json").lower()
    record_id = str(record_id).strip()

    match = df[df[ID_COL] == record_id]

    if match.empty:
        return jsonify({"error": "Record not found", "id": record_id}), 404

    if fmt == "json":
        # Return a single object rather than a list
        obj = match.iloc[0].to_dict()
        return jsonify(obj)
    elif fmt == "csv":
        return dataframe_to_csv(match.iloc[:1])
    else:
        return jsonify({"error": "Invalid format. Use format=json or format=csv"}), 400


if __name__ == "__main__":
    app.run(debug=True)
