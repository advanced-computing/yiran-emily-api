from flask import Flask, request, jsonify
import duckdb

app = Flask(__name__)

DB = "duck.db"


def get_db():
    return duckdb.connect(DB)


@app.route("/permits")
def permits():
    con = get_db()
    data = con.execute("""
        SELECT *
        FROM film_permits
        LIMIT 20
    """).fetchdf()
    con.close()

    return data.to_json(orient="records")


@app.route("/users", methods=["POST"])
def add_user():

    data = request.get_json()

    username = data["username"]
    age = data["age"]
    country = data["country"]

    con = get_db()

    con.execute("""
        INSERT INTO users
        VALUES (?, ?, ?)
    """, [username, age, country])

    con.close()

    return {"message": "user added"}


@app.route("/users/stats")
def user_stats():

    con = get_db()

    total = con.execute("""
        SELECT COUNT(*) FROM users
    """).fetchone()[0]

    avg_age = con.execute("""
        SELECT AVG(age) FROM users
    """).fetchone()[0]

    top = con.execute("""
        SELECT country, COUNT(*) as c
        FROM users
        GROUP BY country
        ORDER BY c DESC
        LIMIT 3
    """).fetchall()

    con.close()

    return {
        "number_of_users": total,
        "average_age": avg_age,
        "top_countries": top
    }


if __name__ == "__main__":
    app.run(debug=True)