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
    quantity INTEGER NOT NULL,
    visible BOOLEAN DEFAULT TRUE
);

CREATE TABLE prices (
    product_id INTEGER REFERENCES products,
    price NUMERIC(8,2) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);