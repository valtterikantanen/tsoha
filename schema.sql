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

CREATE TABLE addresses (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users,
    full_name TEXT NOT NULL,
    street_address TEXT NOT NULL,
    zip_code TEXT NOT NULL,
    city TEXT NOT NULL,
    phone_number TEXT NOT NULL,
    email TEXT NOT NULL,
    visible BOOLEAN DEFAULT TRUE
);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users,
    address INTEGER REFERENCES addresses,
    status TEXT DEFAULT 'open',
    sent_at TIMESTAMP
);

CREATE TABLE order_items (
    order_id INTEGER REFERENCES orders,
    product_id INTEGER REFERENCES products,
    quantity INTEGER
);