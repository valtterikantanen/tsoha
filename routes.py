from flask import flash, redirect, render_template, request, session, url_for

from app import app
import addresses
import errors
import orders
import products
import users

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        if users.is_logged_in():
            user_id = users.get_user_id_by_username()
            return render_template(
                "index.html", user_id=user_id, employee=users.is_employee(),
                number_of_items=orders.get_total_number_of_items_in_cart(user_id))
        return render_template("login.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if not users.login(username, password):
            return render_template("login.html")
        user_id = users.get_user_id_by_username()
        return render_template(
            "index.html", user_id=user_id, employee=users.is_employee(),
            number_of_items=orders.get_total_number_of_items_in_cart(user_id))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        if not users.is_logged_in():
            return render_template("register.html")
        return redirect("/")
    if request.method == "POST":
        username = request.form["username"]
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        if not users.register(username, password1, password2):
            return render_template("register.html")
        return redirect("/")

@app.route("/logout")
def logout():
    users.logout()
    return redirect("/")

@app.route("/customers")
def customers():
    if not users.is_employee():
        return errors.authentication_error()
    customers = users.get_all_customers()
    return render_template("customers.html", employee=True, customers=customers)

@app.route("/make-admin/<int:id>")
def make_admin(id):
    if not users.is_employee():
        return errors.authentication_error()
    users.make_admin(id)
    flash(f"Työntekijän oikeudet lisätty käyttäjälle {users.get_username_by_user_id(id)}!")
    return redirect(url_for("customers"))

@app.route("/new-product", methods=["GET", "POST"])
def new_product():
    if request.method == "GET":
        if users.is_employee():
            return render_template("new_product.html", employee=True)
        return errors.authentication_error()
    if request.method == "POST":
        if session["csrf_token"] != request.form["csrf_token"]:
            abort(403)
        if not users.is_employee():
            return errors.authentication_error()
        name = request.form["name"]
        description = request.form["description"]
        quantity = request.form["quantity"]
        price = request.form["price"]
        product_id = products.add_product(name, quantity, price, description)
        if not product_id:
            return render_template(
                "new_product.html", employee=True, name=name, description=description,
                quantity=quantity, price=price)
        return redirect(url_for("product", id=product_id))

@app.route("/all-products", methods=["GET", "POST"])
def all_products():
    if not users.is_logged_in():
        return errors.authentication_error()
    order = request.form["order"] if request.method == "POST" else "alpha-asc"
    if request.method == "POST" and session["csrf_token"] != request.form["csrf_token"]:
        abort(403)
    user_id = users.get_user_id_by_username()
    number_of_items = orders.get_total_number_of_items_in_cart(user_id)
    return render_template(
        "all_products.html", products=products.all_products(order), user_id=user_id,
        employee=users.is_employee(), order=order, number_of_items=number_of_items)

@app.route("/product/<int:id>")
def product(id):
    if not users.is_logged_in():
        return errors.authentication_error()
    user_id = users.get_user_id_by_username()
    return render_template(
        "product.html", id=id, user_id=user_id, product=products.get_product_info(id),
        price_history=products.get_price_history(id), employee=users.is_employee(),
        number_of_items=orders.get_total_number_of_items_in_cart(user_id))

@app.route("/edit-product/<int:id>", methods=["GET", "POST"])
def edit_product(id):
    if request.method == "GET":
        if not users.is_employee():
            return errors.authentication_error()
        return render_template(
            "edit_product.html", id=id, product=products.get_product_info(id), employee=True)
    if request.method == "POST":
        if session["csrf_token"] != request.form["csrf_token"]:
            abort(403)
        if not users.is_employee():
            return errors.authentication_error()
        name = request.form["name"]
        quantity = request.form["quantity"]
        price = request.form["price"]
        description = request.form["description"]
        if products.edit_product(id, name, quantity, price, description):
            flash("Tuotteen tiedot päivitetty!", category="success")
            return redirect(url_for("product", id=id))
        return render_template(
            "edit_product.html", id=id, product=products.get_product_info(id), employee=True)

@app.route("/account/<int:id>")
def account(id):
    user_id = users.get_user_id_by_username()
    if user_id != id and not users.is_employee():
        return errors.authentication_error()
    if users.is_employee(id):
        return errors.page_not_found()
    username = users.get_username_by_user_id(id)
    number_of_items = orders.get_total_number_of_items_in_cart(id)
    user_addresses = addresses.get_all_addresses(id)
    open_orders = orders.get_open_orders(id)
    open_order_ids = orders.get_open_order_ids(id)
    open_order_grand_totals, delivered_order_grand_totals = None, None
    if open_order_ids:
        open_order_grand_totals = []
        for order_id in open_order_ids:
            open_order_grand_totals.append(orders.get_total_sum(order_id[0]))
    delivered_orders = orders.get_delivered_orders(id)
    delivered_order_ids = orders.get_delivered_order_ids(id)
    if delivered_order_ids:
        delivered_order_grand_totals = []
        for order_id in delivered_order_ids:
            delivered_order_grand_totals.append(orders.get_total_sum(order_id[0]))
    return render_template(
        "account.html", employee=users.is_employee(), user_id=id, username=username,
        addresses=user_addresses, number_of_items=number_of_items, open_orders=open_orders,
        open_order_grand_totals=open_order_grand_totals, delivered_orders=delivered_orders,
        delivered_order_grand_totals=delivered_order_grand_totals)

@app.route("/new-address/<int:id>", methods=["GET", "POST"])
def new_address(id):
    if request.method == "GET":
        username = users.get_username_by_user_id(id)
        if not username:
            return errors.page_not_found()
        if id != users.get_user_id_by_username() and not users.is_employee():
            return errors.authentication_error()
        return render_template(
            "new_address.html", user_id=id, employee=users.is_employee(),
            number_of_items=orders.get_total_number_of_items_in_cart(id))
    if request.method == "POST":
        if session["csrf_token"] != request.form["csrf_token"]:
            abort(403)
        if id != users.get_user_id_by_username() and not users.is_employee():
            return errors.authentication_error()
        full_name = request.form["full_name"]
        street_address = request.form["street_address"]
        zip_code = request.form["zip_code"]
        city = request.form["city"].upper()
        phone = request.form["phone_number"]
        email = request.form["email"]
        if addresses.new_address(id, full_name, street_address, zip_code, city, phone, email):
            flash("Uusi osoite lisätty!", category="success")
            return redirect(url_for("account", id=id))
        return render_template(
            "new_address.html", user_id=id, employee=users.is_employee(),
            full_name=full_name, street_address=street_address, zip_code=zip_code,
            city=city, phone_number=phone, email=email)

@app.route("/edit-address/<int:id>", methods=["GET", "POST"])
def edit_address(id):
    if request.method == "GET":
        if not addresses.is_visible(id):
            return errors.page_not_found()
        if addresses.get_address_owner(id) != users.get_user_id_by_username():
            if not users.is_employee():
                return errors.authentication_error()
        user_id = addresses.get_address_owner(id)
        number_of_items = orders.get_total_number_of_items_in_cart(user_id)
        return render_template(
            "edit_address.html", id=id, user_id=user_id, address=addresses.get_address(id),
            employee=users.is_employee(), number_of_items=number_of_items)
    if request.method == "POST":
        if session["csrf_token"] != request.form["csrf_token"]:
            abort(403)
        user_id = int(request.form["address_owner"])
        if user_id != users.get_user_id_by_username() and not users.is_employee():
            return errors.authentication_error()
        full_name = request.form["full_name"]
        street_address = request.form["street_address"]
        zip = request.form["zip_code"]
        city = request.form["city"].upper()
        phone = request.form["phone_number"]
        email = request.form["email"]
        number_of_items = orders.get_total_number_of_items_in_cart(user_id)
        if not addresses.new_address(user_id, full_name, street_address, zip, city, phone, email):
            return render_template(
                "edit_address.html", id=id, user_id=user_id, address=addresses.get_address(id),
                employee=users.is_employee(), number_of_items=number_of_items)
        addresses.delete_address(id)
        flash("Osoitetiedot päivitetty!", category="success")
        return redirect(url_for("account", id=user_id))

@app.route("/delete-address/<int:id>")
def delete_address(id):
    if not addresses.is_visible(id):
        return errors.page_not_found()
    address_owner = addresses.get_address_owner(id)
    if not address_owner or (address_owner != users.get_user_id_by_username()):
        if not users.is_employee():
            return errors.authentication_error()
    addresses.delete_address(id)
    return redirect(url_for("account", id=address_owner))

@app.route("/error")
def error():
    return render_template("error.html")

@app.route("/cart")
def cart():
    if users.is_employee():
        return errors.page_not_found()
    user_id = users.get_user_id_by_username()
    order_id = orders.get_unfinished_order_id(user_id)
    u_addresses = addresses.get_formatted_visible_addresses(addresses.get_all_addresses(user_id))
    if not order_id:
        return render_template(
            "cart.html", user_id=user_id, employee=False, number_of_items=0,
            user_addresses=u_addresses, default_address=orders.get_address_id(order_id))
    products = orders.get_order_items(order_id)
    total_sum = orders.get_total_sum(order_id)
    number_of_items = orders.get_total_number_of_items_in_cart(user_id)
    return render_template(
        "cart.html", user_id=user_id, employee=False, products=products, total_sum=total_sum,
        number_of_items=number_of_items, user_addresses=u_addresses,
        default_address=orders.get_address_id(order_id))

@app.route("/update-quantity", methods=["POST"])
def update_quantity():
    product_id = request.form["product_id"]
    quantity = request.form["quantity"]
    order_id = request.form["order_id"]
    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)
    if users.is_employee():
        return errors.page_not_found()
    if orders.get_order_owner(order_id) != users.get_user_id_by_username():
        return errors.authentication_error()
    orders.update_item_quantity(product_id, quantity, order_id)
    return redirect(url_for("cart"))

@app.route("/add-item-to-cart/<int:product_id>")
def add_item_to_cart(product_id):
    user_id = users.get_user_id_by_username()
    order_id = orders.get_unfinished_order_id(user_id)
    if users.is_employee():
        return errors.page_not_found()
    if not order_id:
        order_id = orders.create_new(user_id)
    orders.add_item(order_id, product_id)
    return redirect(url_for("product", id=product_id))

@app.route("/delete-item/<int:product_id>")
def delete_item(product_id):
    user_id = users.get_user_id_by_username()
    order_id = orders.get_unfinished_order_id(user_id)
    if users.is_employee() or not order_id:
        return errors.page_not_found()
    orders.update_item_quantity(product_id, "0", order_id)
    return redirect(url_for("cart"))

@app.route("/add-address-to-order", methods=["POST"])
def add_address_to_order():
    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)
    address_id = request.form["address"]
    order_id = request.form["order_id"]
    address_owner = addresses.get_address_owner(address_id)
    order_owner = orders.get_order_owner(order_id)
    if address_owner != order_owner and not users.is_employee():
        return errors.authentication_error()
    orders.set_address_to_order(address_id, order_id)
    return redirect(url_for("cart"))

@app.route("/send-order/<int:order_id>")
def send_order(order_id):
    user_id = orders.get_order_owner(order_id)
    if orders.get_order_status(order_id) != "unfinished":
        flash("Tilaus on jo lähetetty!", category="error")
        return redirect(url_for("account", id=user_id))
    if user_id != users.get_user_id_by_username() and not users.is_employee():
        return errors.authentication_error()
    if not orders.get_address_id(order_id):
        flash("Valitse toimitusosoite!", category="error")
        return redirect(url_for("cart"))
    orders.send_order(order_id)
    flash("Tilaus lähetetty!", category="success")
    return redirect(url_for("account", id=user_id))

@app.route("/order/<int:order_id>")
def order(order_id):
    user_id = users.get_user_id_by_username()
    status = orders.get_order_status(order_id)
    if not status or status == "unfinished":
        return errors.page_not_found()
    if orders.get_order_owner(order_id) != user_id and not users.is_employee():
        return errors.authentication_error()
    order_info = orders.get_order_information(order_id)
    grand_total = orders.get_total_sum(order_id)
    address = addresses.get_address(orders.get_address_id(order_id))
    sent_at = orders.get_order_time(order_id)
    number_of_items = orders.get_total_number_of_items_in_cart(user_id)
    return render_template(
        "order.html", order_id=order_id, user_id=user_id, employee=users.is_employee(),
        number_of_items=number_of_items, order_info=order_info, grand_total=grand_total,
        address=address, sent_at=sent_at, status=status)

@app.route("/all-orders")
def all_orders():
    if not users.is_employee():
        return errors.authentication_error()
    open_orders = orders.get_all_open_orders()
    delivered_orders = orders.get_all_delivered_orders()
    return render_template(
        "all_orders.html", employee=True, open_orders=open_orders,
        delivered_orders=delivered_orders)

@app.route("/handle-order/<int:order_id>")
def handle_order(order_id):
    if not users.is_employee():
        return errors.authentication_error()
    if not orders.get_order_owner(order_id):
        return errors.page_not_found()
    orders.handle_order(order_id)
    flash("Tilaus käsitelty!", category="success")
    return redirect(url_for("order", order_id=order_id))
