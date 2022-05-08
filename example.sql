DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS prices CASCADE;
DROP TABLE IF EXISTS addresses CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS order_items CASCADE;

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
    address_id INTEGER REFERENCES addresses,
    status TEXT DEFAULT 'unfinished',
    sent_at TIMESTAMP
);

CREATE TABLE order_items (
    order_id INTEGER REFERENCES orders,
    product_id INTEGER REFERENCES products,
    quantity INTEGER
);

INSERT INTO users (username, password, role) VALUES ('admin', 'pbkdf2:sha256:260000$w0Lwpe72mAeqcJoH$cedd94f29212df38f5f43e8526f803b003d0c75365caf24659e7919e176ad776', 'employee');
INSERT INTO users (username, password) VALUES ('customer', 'pbkdf2:sha256:260000$MJ2MpzlF8gcwGs7L$6fc9b8b502a43a167e624e82e6eec50a0a30ee9ad4b83413763fcaaf90cf225c');

INSERT INTO products (name, description, quantity) VALUES ('Kirves', 'Hyvä kirves kovaan käyttöön!', 6);
INSERT INTO products (name, quantity) VALUES ('Vasara', 7);
INSERT INTO products (name, quantity) VALUES ('Mittanauha 3 m', 3);
INSERT INTO products (name, quantity) VALUES ('Porakone', 2);
INSERT INTO products (name, quantity) VALUES ('Kuulosuojain radiolla', 3);
INSERT INTO products (name, quantity) VALUES ('Kaksipuolinen teippi 15 m', 0);
INSERT INTO products (name, description, quantity) VALUES ('HDMI-kaapeli 1,8 m', 'Korkealaatuinen ja kestävä HDMI-kaapeli.', 14);
INSERT INTO products (name, quantity) VALUES ('Öljylamppu', 8);

INSERT INTO prices (product_id, price, created_at) VALUES (1, 45.90, '2022-04-16 16:58:44.30592');
INSERT INTO prices (product_id, price, created_at) VALUES (2, 10.90, '2022-04-16 16:58:44.510906');
INSERT INTO prices (product_id, price, created_at) VALUES (3, 7.90, '2022-04-16 16:58:44.715142');
INSERT INTO prices (product_id, price, created_at) VALUES (4, 129.90, '2022-04-16 16:58:44.920403');
INSERT INTO prices (product_id, price, created_at) VALUES (5, 69.90, '2022-04-16 16:58:45.125193');
INSERT INTO prices (product_id, price, created_at) VALUES (6, 4.50, '2022-04-16 16:58:45.329902');
INSERT INTO prices (product_id, price, created_at) VALUES (7, 33.90, '2022-04-16 16:58:45.534922');
INSERT INTO prices (product_id, price, created_at) VALUES (8, 39.90, '2022-04-16 16:58:45.701891');

INSERT INTO addresses (user_id, full_name, street_address, zip_code, city, phone_number, email) VALUES (2, 'Matti Meikäläinen', 'Pietari Kalmin katu 5', '00560', 'HELSINKI', '0501234567', 'matti@meikalainen.com');
INSERT INTO addresses (user_id, full_name, street_address, zip_code, city, phone_number, email) VALUES (2, 'Matti Meikäläinen', 'Gustaf Hällströmin katu 2', '00560', 'HELSINKI', '0501234567', 'matti@meikalainen.com');
INSERT INTO addresses (user_id, full_name, street_address, zip_code, city, phone_number, email, visible) VALUES (2, 'Matti Meikäläinen', 'A. I. Virtasen aukio 1', '00560', 'HELSINKI', '0501234567', 'matti@meikalainen.com', FALSE);

INSERT INTO orders (user_id, address_id) VALUES (2, 1);

INSERT INTO order_items (order_id, product_id, quantity) VALUES (1, 1, 1);
INSERT INTO order_items (order_id, product_id, quantity) VALUES (1, 2, 3);
INSERT INTO order_items (order_id, product_id, quantity) VALUES (1, 3, 2);
INSERT INTO order_items (order_id, product_id, quantity) VALUES (1, 4, 1);