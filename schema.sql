CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE,
    password TEXT NOT NULL,
    role TEXT DEFAULT 'customer'
);

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    price NUMERIC(8,2) NOT NULL,
    quantity INTEGER NOT NULL
);