CREATE TABLE film_permits AS
SELECT *
FROM read_csv_auto(
    'Film_Permits_20260306.csv',
    delim=';',
    header=true
);

CREATE TABLE users (
    username VARCHAR,
    age INTEGER,
    country VARCHAR
);