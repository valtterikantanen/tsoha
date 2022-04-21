from flask import flash, session

from db import db

def get_open_order_id(user_id):
    query = "SELECT id FROM orders WHERE user_id=:user_id AND status='open'"
    order_id = db.session.execute(query, {"user_id": user_id}).fetchone()
    return order_id[0] if order_id else None

def get_order_items(order_id):
    query = "SELECT A.id, A.name, O.quantity, O.order_id, A.quantity AS maximum, B.price, O.quantity * B.price AS subtotal FROM order_items O, products A, (SELECT DISTINCT ON (product_id) product_id, price FROM prices ORDER BY product_id, created_at DESC) B WHERE O.order_id=:order_id AND A.id=O.product_id AND B.product_id=O.product_id"
    products = db.session.execute(query, {"order_id": order_id}).fetchall()
    return products

def get_total_sum(order_id):
    query = "SELECT SUM(A.quantity * B.price) FROM order_items A, prices B WHERE A.product_id=B.product_id AND A.order_id=:order_id"
    total_sum =  db.session.execute(query, {"order_id": order_id}).fetchone()[0]
    return total_sum

def update_item_quantity(product_id, quantity, order_id):
    if quantity == "0":
        query = "DELETE FROM order_items WHERE product_id=:product_id AND order_id=:order_id"
        db.session.execute(query, {"product_id": product_id, "order_id": order_id})
    else:
        query = "UPDATE order_items SET quantity=:quantity WHERE product_id=:product_id AND order_id=:order_id"
        db.session.execute(query, {"quantity": quantity, "product_id": product_id, "order_id": order_id})
    db.session.commit()