from db import db
import products

def create_new(user_id):
    query = "INSERT INTO orders (user_id, status) VALUES (:user_id, 'open') RETURNING id"
    order_id = db.session.execute(query, {"user_id": user_id}).fetchone()[0]
    db.session.commit()
    return order_id

def get_order_owner(order_id):
    query = "SELECT user_id FROM orders WHERE id=:order_id"
    user_id = db.session.execute(query, {"order_id": order_id}).fetchone()
    return user_id[0] if user_id else None

def get_open_order_id(user_id):
    query = "SELECT id FROM orders WHERE user_id=:user_id AND status='open'"
    order_id = db.session.execute(query, {"user_id": user_id}).fetchone()
    return order_id[0] if order_id else None

def get_order_items(order_id):
    query = "SELECT A.id, A.name, O.quantity, O.order_id, A.quantity AS maximum, B.price, O.quantity * B.price AS subtotal FROM order_items O, products A, (SELECT DISTINCT ON (product_id) product_id, price FROM prices ORDER BY product_id, created_at DESC) B WHERE O.order_id=:order_id AND A.id=O.product_id AND B.product_id=O.product_id"
    products = db.session.execute(query, {"order_id": order_id}).fetchall()
    return products

def get_total_sum(order_id):
    query = "SELECT SUM(A.quantity * B.price) FROM order_items A, (SELECT DISTINCT ON (product_id) product_id, price FROM prices ORDER BY product_id, created_at DESC) B WHERE A.product_id=B.product_id AND A.order_id=:order_id"
    total_sum = db.session.execute(query, {"order_id": order_id}).fetchone()[0]
    return total_sum

def get_total_number_of_items_in_cart(user_id):
    order_id = get_open_order_id(user_id)
    query = "SELECT SUM(quantity) FROM order_items WHERE order_id=:order_id"
    total_amount = db.session.execute(query, {"order_id": order_id}).fetchone()
    return total_amount[0] if total_amount else None

def get_number_of_items(order_id, product_id):
    query = "SELECT quantity FROM order_items WHERE order_id=:order_id AND product_id=:product_id"
    quantity = db.session.execute(query, {"order_id": order_id, "product_id": product_id}).fetchone()
    return quantity[0] if quantity else 0

def add_item(order_id, product_id):
    current_quantity = get_number_of_items(order_id, product_id)
    maximum = products.get_current_quantity(product_id)
    if maximum < current_quantity + 1:
        return False
    if current_quantity == 0:
        query = "INSERT INTO order_items (order_id, product_id, quantity) VALUES (:order_id, :product_id, 1)"
        db.session.execute(query, {"order_id": order_id, "product_id": product_id})
        db.session.commit()
    else:
        update_item_quantity(product_id, current_quantity + 1, order_id)
    return True

def update_item_quantity(product_id, quantity, order_id):
    maximum = products.get_current_quantity(product_id)
    if maximum < int(quantity):
        return False
    if quantity == "0":
        query = "DELETE FROM order_items WHERE product_id=:product_id AND order_id=:order_id"
        db.session.execute(query, {"product_id": product_id, "order_id": order_id})
    else:
        query = "UPDATE order_items SET quantity=:quantity WHERE product_id=:product_id AND order_id=:order_id"
        db.session.execute(query, {"quantity": quantity, "product_id": product_id, "order_id": order_id})
    db.session.commit()
    return True

def set_address_to_order(address_id, order_id):
    query = "UPDATE orders SET address_id=:address_id WHERE id=:order_id"
    db.session.execute(query, {"address_id": address_id, "order_id": order_id})
    db.session.commit()

def get_address_id(order_id):
    query = "SELECT address_id FROM orders WHERE id=:order_id"
    order_id = db.session.execute(query, {"order_id": order_id}).fetchone()
    return order_id[0] if order_id else None

def send_order(order_id):
    query = "UPDATE orders SET status='sent' WHERE id=:order_id"
    db.session.execute(query, {"order_id": order_id})
    db.session.commit()