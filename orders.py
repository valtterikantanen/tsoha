from db import db
import products

def create_new(user_id):
    query = "INSERT INTO orders (user_id) VALUES (:user_id) RETURNING id"
    order_id = db.session.execute(query, {"user_id": user_id}).fetchone()[0]
    db.session.commit()
    return order_id

def get_order_owner(order_id):
    query = "SELECT user_id FROM orders WHERE id=:order_id"
    user_id = db.session.execute(query, {"order_id": order_id}).fetchone()
    return user_id[0] if user_id else None

def get_order_time(order_id):
    query = "SELECT sent_at FROM orders WHERE id=:order_id"
    sent_at = db.session.execute(query, {"order_id": order_id}).fetchone()[0]
    return sent_at

def get_unfinished_order_id(user_id):
    query = "SELECT id FROM orders WHERE user_id=:user_id AND status='unfinished'"
    order_id = db.session.execute(query, {"user_id": user_id}).fetchone()
    return order_id[0] if order_id else None

def get_order_items(order_id):
    query = "SELECT A.id, A.name, O.quantity, O.order_id, A.quantity AS maximum, B.price, " \
            "O.quantity * B.price AS subtotal FROM order_items O, products A, " \
            "(SELECT DISTINCT ON (product_id) product_id, price FROM prices " \
            "ORDER BY product_id, created_at DESC) B WHERE O.order_id=:order_id " \
            "AND A.id=O.product_id AND B.product_id=O.product_id"
    product_items = db.session.execute(query, {"order_id": order_id}).fetchall()
    return product_items

def get_order_item_ids(order_id):
    query = "SELECT product_id FROM order_items WHERE order_id=:order_id ORDER BY product_id"
    product_ids = db.session.execute(query, {"order_id": order_id}).fetchall()
    return product_ids

def get_total_sum(order_id):
    query = "SELECT SUM(I.quantity * B.price) FROM order_items I, (SELECT DISTINCT ON " \
            "(product_id) product_id, price FROM prices WHERE created_at <= (SELECT COALESCE " \
            "(sent_at, NOW()) FROM orders WHERE id=:order_id) ORDER BY product_id, " \
            "created_at DESC) B WHERE I.product_id=B.product_id AND I.order_id=:order_id"
    total_sum = db.session.execute(query, {"order_id": order_id}).fetchone()[0]
    return total_sum

def get_total_number_of_items_in_cart(user_id):
    order_id = get_unfinished_order_id(user_id)
    query = "SELECT SUM(quantity) FROM order_items WHERE order_id=:order_id"
    total_amount = db.session.execute(query, {"order_id": order_id}).fetchone()
    return total_amount[0] if total_amount else None

def get_number_of_items(order_id, product_id):
    query = "SELECT quantity FROM order_items WHERE order_id=:order_id AND product_id=:product_id"
    quantity = db.session.execute(
        query, {"order_id": order_id, "product_id": product_id}).fetchone()
    return quantity[0] if quantity else 0

def add_item(order_id, product_id):
    current_quantity = get_number_of_items(order_id, product_id)
    maximum = products.get_current_quantity(product_id)
    if maximum < current_quantity + 1:
        return False
    if current_quantity == 0:
        query = "INSERT INTO order_items (order_id, product_id, quantity) " \
                "VALUES (:order_id, :product_id, 1)"
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
        query = "UPDATE order_items SET quantity=:quantity " \
                "WHERE product_id=:product_id AND order_id=:order_id"
        db.session.execute(query, {"quantity": quantity, "product_id": product_id,
                                   "order_id": order_id})
    db.session.commit()
    return True

def set_address_to_order(address_id, order_id):
    query = "UPDATE orders SET address_id=:address_id WHERE id=:order_id"
    db.session.execute(query, {"address_id": address_id, "order_id": order_id})
    db.session.commit()

def get_address_id(order_id):
    query = "SELECT address_id FROM orders WHERE id=:order_id"
    address_id = db.session.execute(query, {"order_id": order_id}).fetchone()
    return address_id[0] if address_id else None

def send_order(order_id):
    product_ids = get_order_item_ids(order_id)
    for product_id in product_ids:
        quantity_in_order = get_number_of_items(order_id, product_id[0])
        quantity_in_stock = products.get_current_quantity(product_id[0])
        query = "UPDATE products SET quantity=:quantity WHERE id=:product_id"
        db.session.execute(query, {"quantity": quantity_in_stock - quantity_in_order,
                                   "product_id": product_id[0]})
    query = "UPDATE orders SET status='open', sent_at=NOW() WHERE id=:order_id"
    db.session.execute(query, {"order_id": order_id})
    db.session.commit()

def get_order_information(order_id):
    query = "SELECT A.id, A.name, B.price, I.quantity, B.price*I.quantity AS subtotal " \
            "FROM products A, orders O, order_items I, (SELECT DISTINCT ON (product_id) " \
            "product_id, price FROM prices WHERE created_at <= (SELECT sent_at FROM orders " \
            "WHERE id=:order_id) ORDER BY product_id, created_at DESC) B WHERE A.id=B.product_id " \
            "AND O.id=:order_id AND O.id=I.order_id AND A.id=I.product_id ORDER BY subtotal DESC"
    order_information = db.session.execute(query, {"order_id": order_id}).fetchall()
    return order_information

def get_open_orders(user_id):
    query = "SELECT id, sent_at FROM orders WHERE user_id=:user_id " \
            "AND status='open' ORDER BY sent_at DESC"
    open_orders = db.session.execute(query, {"user_id": user_id}).fetchall()
    return open_orders if open_orders else None

def get_all_open_orders():
    query = "SELECT O.id AS order_id, O.sent_at, O.user_id, U.username FROM orders O, users U " \
            "WHERE O.user_id=U.id AND O.status='open'"
    open_orders = db.session.execute(query).fetchall()
    return open_orders if open_orders else None

def get_open_order_ids(user_id):
    query = "SELECT id FROM orders WHERE user_id=:user_id AND status='open' ORDER BY sent_at DESC"
    open_order_ids = db.session.execute(query, {"user_id": user_id}).fetchall()
    return open_order_ids

def get_delivered_orders(user_id):
    query = "SELECT id, sent_at FROM orders WHERE user_id=:user_id " \
            "AND status='delivered' ORDER BY sent_at DESC"
    delivered_orders = db.session.execute(query, {"user_id": user_id}).fetchall()
    return delivered_orders if delivered_orders else None

def get_all_delivered_orders():
    query = "SELECT O.id AS order_id, O.sent_at, O.user_id, U.username " \
            "FROM orders O, users U WHERE O.user_id=U.id AND O.status='delivered'"
    open_orders = db.session.execute(query).fetchall()
    return open_orders if open_orders else None

def get_delivered_order_ids(user_id):
    query = "SELECT id FROM orders WHERE user_id=:user_id " \
            "AND status='delivered' ORDER BY sent_at DESC"
    delivered_order_ids = db.session.execute(query, {"user_id": user_id}).fetchall()
    return delivered_order_ids

def get_order_status(order_id):
    query = "SELECT status FROM orders WHERE id=:order_id"
    status = db.session.execute(query, {"order_id": order_id}).fetchone()
    return status[0] if status else None

def handle_order(order_id):
    query = "UPDATE orders SET status='delivered' WHERE id=:order_id"
    db.session.execute(query, {"order_id": order_id})
    db.session.commit()
