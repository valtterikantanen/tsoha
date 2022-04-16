from flask import flash

from db import db

def add_product(name, description, quantity, price):
    errors = False

    if not name.strip():
        flash("Syötä tuotteen nimi", category="error")
        errors = True

    if len(name) > 150:
        flash("Tuotteen nimi voi olla enintään 150 merkkiä pitkä", category="error")
        errors = True

    if len(description) > 1000:
        flash("Tuotteen kuvaus voi olla enintään 1 000 merkkiä pitkä", category="error")
        errors = True

    try:
        quantity = int(quantity)
        if quantity < 0:
            flash("Tuotteen saldo ei voi olla negatiivinen", category="error")
    except ValueError:
        flash("Syötä varastosaldo", category="error")
        errors = True

    try:
        price = float(price)
        if not 0 <= price <= 999_999.99:
            flash("Tuotteen hinnan on oltava välillä 0,00–999 999,99 €", category="error")
    except ValueError:
        flash("Syötä hinta", category="error")
        errors = True

    if errors:
        return False
    
    query = "INSERT INTO products (name, description, quantity) VALUES (:name, :description, :quantity) RETURNING id"
    product_id = db.session.execute(query, {"name": name, "description": description, "quantity": quantity}).fetchone()[0]
    query = "INSERT INTO prices (product_id, price) VALUES (:product_id, :price)"
    db.session.execute(query, {"product_id": product_id, "price": price})
    db.session.commit()
    flash("Tuote lisätty!", category="success")
    return product_id

def all_products(order_option):
    options = {
        "price-desc": "ORDER BY B.price DESC",
        "price-asc": "ORDER BY B.price",
        "alpha-asc": 'ORDER BY A.name COLLATE "fi_FI"',
        "alpha-desc": 'ORDER BY A.name COLLATE "fi_FI" DESC'
    }
    query = f"SELECT A.id, A.name, A.description, B.price, A.quantity FROM products A, (SELECT DISTINCT ON (product_id) product_id, price FROM prices ORDER BY product_id, created_at DESC) B WHERE A.id=B.product_id AND A.visible=TRUE {options[order_option]}"
    products = db.session.execute(query).fetchall()
    return products

def get_product_info(id):
    query = "SELECT A.name, A.description, B.price, A.quantity FROM products A, prices B WHERE A.id=:id AND B.product_id=:id ORDER BY B.created_at DESC LIMIT 1"
    product = db.session.execute(query, {"id": id}).fetchone()
    return product

def get_price_history(id):
    query = "SELECT price, created_at FROM prices WHERE product_id=:id ORDER BY created_at DESC"
    price_history = db.session.execute(query, {"id": id}).fetchall()
    return price_history

def edit_product(id, name, quantity, price, description):
    query = "UPDATE products SET name=:name, quantity=:quantity, description=:description WHERE id=:id"
    db.session.execute(query, {"name": name, "quantity": quantity, "description": description, "id": id})
    db.session.commit()
    query = "SELECT price FROM prices WHERE product_id=:id ORDER BY created_at DESC LIMIT 1"
    current_price = db.session.execute(query, {"id": id}).fetchone()[0]
    if float(current_price) != float(price):
        query = "INSERT INTO prices (product_id, price) VALUES (:product_id, :price)"
        db.session.execute(query, {"product_id": id, "price": price})
        db.session.commit()