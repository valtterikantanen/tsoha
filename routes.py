from flask import flash, redirect, render_template, request, url_for

from app import app
from db import db
import addresses
import users

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        if users.is_logged_in():
            return render_template("index.html", id=users.get_user_id_by_username(), employee=users.is_employee())
        return render_template("login.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if not users.login(username, password):
            return render_template("login.html")
        return render_template("index.html", id=users.get_user_id_by_username(), employee=users.is_employee())
        
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
    customers = users.get_all_customers()
    if not customers and len(customers) != 0:
        flash("Sinulla ei ole oikeutta nähdä sivua", category="error")
        return redirect("/error")
    return render_template("customers.html", employee=users.is_employee(), customers=customers)

@app.route("/make-admin/<int:id>")
def make_admin(id):
    if not users.make_admin(id):
        flash("Sinulla ei ole oikeutta nähdä sivua", category="error")
        return redirect("/error")
    flash(f"Työntekijän oikeudet lisätty käyttäjälle {users.get_username_by_user_id(id)}!")
    return redirect(url_for("customers"))

@app.route("/new-product", methods=["GET", "POST"])
def new_product():
    if request.method == "GET":
        if users.is_employee():
            return(render_template("new_product.html", employee=users.is_employee()))
        flash("Sinulla ei ole oikeutta nähdä sivua", category="error")
        return redirect("/error")
    if request.method == "POST":
        errors = False
        name = request.form["name"]
        description = request.form["description"]

        if not name.strip():
            flash("Syötä tuotteen nimi", category="error")
            errors = True
        try:
            quantity = int(request.form["quantity"])
        except ValueError:
            flash("Syötä varastosaldo", category="error")
            errors = True
        try:
            price = float(request.form["price"])
        except ValueError:
            flash("Syötä hinta", category="error")
            errors = True
        if errors:
            return render_template("new_product.html", employee=users.is_employee())
        
        query = "INSERT INTO products (name, description, quantity) VALUES (:name, :description, :quantity) RETURNING id"
        result = db.session.execute(query, {"name": name, "description": description, "quantity": quantity})
        product_id = result.fetchone()[0]
        query = "INSERT INTO prices (product_id, price) VALUES (:product_id, :price)"
        db.session.execute(query, {"product_id": product_id, "price": price})
        db.session.commit()
        flash("Tuote lisätty!", category="success")
        return redirect(url_for("product", id=id))

@app.route("/all-products", methods=["GET", "POST"])
def all_products():
    options = {
        "price-desc": "ORDER BY B.price DESC",
        "price-asc": "ORDER BY B.price",
        "alpha-asc": 'ORDER BY A.name COLLATE "fi_FI"',
        "alpha-desc": 'ORDER BY A.name COLLATE "fi_FI" DESC'
    }
    if not users.is_logged_in():
        flash("Sinulla ei ole oikeutta nähdä sivua", category="error")
        return redirect("/error")
    order = request.form["order"] if request.method == "POST" else "alpha-asc"
    query = f"SELECT A.id, A.name, A.description, B.price, A.quantity FROM products A, (SELECT DISTINCT ON (product_id) product_id, price FROM prices ORDER BY product_id, created_at DESC) B WHERE A.id=B.product_id AND A.visible=TRUE {options[order]}"
    result = db.session.execute(query)
    products = result.fetchall()
    return render_template("all_products.html", products=products, id=users.get_user_id_by_username(), employee=users.is_employee())

@app.route("/product/<int:id>")
def product(id):
    if not users.is_logged_in():
        flash("Sinulla ei ole oikeutta nähdä sivua", category="error")
        return redirect("/error")
    query = "SELECT A.name, A.description, B.price, A.quantity FROM products A, prices B WHERE A.id=:id AND B.product_id=:id ORDER BY B.created_at DESC LIMIT 1"
    product = db.session.execute(query, {"id": id}).fetchone()
    query = "SELECT price, created_at FROM prices WHERE product_id=:id ORDER BY created_at DESC"
    price_history = db.session.execute(query, {"id": id}).fetchall()
    return render_template("product.html", id=id, product=product, employee=users.is_employee(), price_history=price_history)

@app.route("/edit-product/<int:id>", methods=["GET", "POST"])
def edit_product(id):
    if request.method == "GET":
        if not users.is_employee():
            flash("Sinulla ei ole oikeutta nähdä sivua", category="error")
            return redirect("/error")
        query = "SELECT A.name, A.description, B.price, A.quantity FROM products A, prices B WHERE A.id=:id AND B.product_id=:id ORDER BY B.created_at DESC LIMIT 1"
        product = db.session.execute(query, {"id": id}).fetchone()
        return render_template("edit_product.html", id=id, product=product, employee=users.is_employee())
    if request.method == "POST":
        name = request.form["name"]
        quantity = request.form["quantity"]
        price = request.form["price"]
        description = request.form["description"]
        query = "UPDATE products SET name=:name, quantity=:quantity, description=:description WHERE id=:id"
        db.session.execute(query, {"name": name, "quantity": quantity, "description": description, "id": id})
        db.session.commit()
        query = "SELECT price FROM prices WHERE product_id=:id ORDER BY created_at DESC LIMIT 1"
        current_price = db.session.execute(query, {"id": id}).fetchone()[0]
        if float(current_price) != float(price):
            query = "INSERT INTO prices (product_id, price) VALUES (:product_id, :price)"
            db.session.execute(query, {"product_id": id, "price": price})
            db.session.commit()
        flash("Tuotteen tiedot päivitetty!", category="success")
        return redirect(url_for("product", id=id))

@app.route("/account/<int:id>")
def account(id):
    user_id = users.get_user_id_by_username()
    if user_id != id and not users.is_employee():
        flash("Sinulla ei ole oikeutta nähdä sivua", category="error")
        return redirect("/error")
    if users.is_employee(id):
        flash("Käyttäjäsivua ei ole olemassa.", category="error")
        return redirect("/error")
    return render_template("account.html", employee=users.is_employee(), id=id, username=users.get_username_by_user_id(id), addresses=addresses.get_all_addresses(id))

@app.route("/new-address/<int:id>", methods=["GET", "POST"])
def new_address(id):
    if request.method == "GET":
        if not users.is_logged_in():
            flash("Sinulla ei ole oikeutta nähdä sivua", category="error")
            return redirect("/error")
        return render_template("new_address.html", id=id, employee=users.is_employee())
    if request.method == "POST":
        full_name = request.form["full_name"]
        street_address = request.form["street_address"]
        zip_code = request.form["zip_code"]
        city = request.form["city"].upper()
        phone_number = request.form["phone_number"]
        email = request.form["email"]
        addresses.new_address(id, full_name, street_address, zip_code, city, phone_number, email)
        flash("Uusi osoite lisätty!", category="success")
        return redirect(url_for("account", id=id))

@app.route("/edit-address/<int:id>", methods=["GET", "POST"])
def edit_address(id):
    if request.method == "GET":
        if not users.is_logged_in():
            flash("Sinulla ei ole oikeutta nähdä sivua", category="error")
            return redirect("/error")
        return render_template("edit_address.html", id=id, address=addresses.get_address(id), employee=users.is_employee())
    if request.method == "POST":
        full_name = request.form["full_name"]
        street_address = request.form["street_address"]
        zip_code = request.form["zip_code"]
        city = request.form["city"].upper()
        phone_number = request.form["phone_number"]
        email = request.form["email"]
        address_owner = request.form["address_owner"]
        addresses.new_address(address_owner, full_name, street_address, zip_code, city, phone_number, email)
        addresses.delete_address(id)
        flash("Osoitetiedot päivitetty!", category="success")
        return redirect(url_for("account", id=address_owner))

@app.route("/delete-address/<int:id>")
def delete_address(id):
    if not users.is_logged_in():
        flash("Sinulla ei ole oikeutta nähdä sivua", category="error")
        return redirect("/error")
    address_owner = addresses.get_address_owner(id)
    if not address_owner:
        flash("Osoitetta ei löytynyt", category="error")
        return redirect("/error") 
    if address_owner != users.get_user_id_by_username() and not users.is_employee():
        flash("Sinulla ei ole oikeutta nähdä sivua", category="error")
        return redirect("/error")
    addresses.delete_address(id)
    return redirect(url_for("account", id=address_owner))

@app.route("/error")
def error():
    return render_template("error.html")