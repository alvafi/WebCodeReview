CREATE TABLE IF NOT EXISTS performances (
    id SERIAL PRIMARY KEY,
    name VARCHAR(500) NOT NULL,
    date timestamp NOT NULL
);