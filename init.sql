ATTACH DATABASE 'duck.db' AS mydb;

DROP TABLE IF EXISTS mydb.film_permits;
DROP TABLE IF EXISTS mydb.users;

CREATE TABLE mydb.film_permits AS
SELECT *
FROM read_csv_auto(
    'Film_Permits_20260306.csv',
    delim=';',
    header=true
);

CREATE TABLE mydb.users (
    username VARCHAR,
    age INTEGER,
    country VARCHAR
);