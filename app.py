from os import getenv
import re

from flask import Flask
from flask import flash, redirect, render_template, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = getenv("SECRET_KEY")

db = SQLAlchemy(app)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        if is_logged_in():
            return render_template("index.html", id=get_current_users_id(), employee=is_employee())
        return render_template("login.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        query = "SELECT password FROM users WHERE username=:username"
        result = db.session.execute(query, {"username": username})
        user = result.fetchone()
        if not user:
            flash("Käyttäjää ei löytynyt", category="error")
            return render_template("login.html")
        if check_password_hash(user.password, password):
            session["username"] = username
            return render_template("index.html", id=get_current_users_id(), employee=is_employee())
        flash("Väärä salasana", category="error")
        return render_template("login.html")
        
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        if not is_logged_in():
            return render_template("register.html")
        return redirect("/")
    if request.method == "POST":
        errors = False
        username = request.form["username"]
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        if not re.match("^[a-zA-Z0-9]+$", username):
            flash("Käyttäjätunnus voi sisältää vain kirjaimia a–z ja numeroita 0–9", category="error")
            errors = True
        if len(password1) < 5:
            flash("Salasanassa tulee olla vähintään viisi merkkiä", category="error")
            errors = True
        if password1 != password2:
            flash("Salasanat eivät täsmää", category="error")
            errors = True
        query = "SELECT COUNT(*) FROM users WHERE LOWER(username)=:username"
        result = db.session.execute(query, {"username": username.lower()})
        user_count = result.fetchone()[0]
        if user_count != 0:
            flash("Käyttäjätunnus on jo käytössä", category="error")
            errors = True
        if errors:
            return render_template("register.html")
        query = "INSERT INTO users (username, password) VALUES (:username, :password)"
        db.session.execute(query, {"username": username, "password": generate_password_hash(password1)})
        db.session.commit()
        session["username"] = username
        return redirect("/")

def is_employee():
    try:
        username = session["username"]
        query = "SELECT role FROM users WHERE username=:username"
        role = db.session.execute(query, {"username": username}).fetchone()[0]
        return role == "employee"
    except:
        return False

def user_is_employee(user_id):
    query = "SELECT role FROM users WHERE id=:id"
    role = db.session.execute(query, {"id": user_id}).fetchone()[0]
    return role == "employee"

def is_logged_in():
    return session.get("username")

def get_current_users_id():
    username = is_logged_in()
    if not username:
        return None
    return get_user_id_by_username(username)

def get_user_id_by_username(username):
    query = "SELECT id FROM users WHERE username=:username"
    user_id = db.session.execute(query, {"username": username}).fetchone()[0]
    return user_id

def get_username_by_user_id(user_id):
    query = "SELECT username FROM users WHERE id=:user_id"
    username = db.session.execute(query, {"user_id": user_id}).fetchone()[0]
    return username

@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")

@app.route("/new-product", methods=["GET", "POST"])
def new_product():
    if request.method == "GET":
        if is_employee():
            return(render_template("new_product.html", employee=is_employee()))
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
            return render_template("new_product.html", employee=is_employee())
        
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
    if not is_logged_in():
        flash("Sinulla ei ole oikeutta nähdä sivua", category="error")
        return redirect("/error")
    order = request.form["order"] if request.method == "POST" else "alpha-asc"
    query = f"SELECT A.id, A.name, A.description, B.price, A.quantity FROM products A, (SELECT DISTINCT ON (product_id) product_id, price FROM prices ORDER BY product_id, created_at DESC) B WHERE A.id=B.product_id AND A.visible=TRUE {options[order]}"
    result = db.session.execute(query)
    products = result.fetchall()
    return render_template("all_products.html", products=products, id=get_current_users_id(), employee=is_employee())

@app.route("/product/<int:id>")
def product(id):
    if not is_logged_in():
        flash("Sinulla ei ole oikeutta nähdä sivua", category="error")
        return redirect("/error")
    query = "SELECT A.name, A.description, B.price, A.quantity FROM products A, prices B WHERE A.id=:id AND B.product_id=:id ORDER BY B.created_at DESC LIMIT 1"
    product = db.session.execute(query, {"id": id}).fetchone()
    query = "SELECT price, created_at FROM prices WHERE product_id=:id ORDER BY created_at DESC"
    price_history = db.session.execute(query, {"id": id}).fetchall()
    return render_template("product.html", id=id, product=product, employee=is_employee(), price_history=price_history)

@app.route("/edit-product/<int:id>", methods=["GET", "POST"])
def edit_product(id):
    if request.method == "GET":
        if not is_employee():
            flash("Sinulla ei ole oikeutta nähdä sivua", category="error")
            return redirect("/error")
        query = "SELECT A.name, A.description, B.price, A.quantity FROM products A, prices B WHERE A.id=:id AND B.product_id=:id ORDER BY B.created_at DESC LIMIT 1"
        product = db.session.execute(query, {"id": id}).fetchone()
        return render_template("edit_product.html", id=id, product=product, employee=is_employee())
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
    user_id = get_current_users_id()
    if user_id != id and not is_employee():
        flash("Sinulla ei ole oikeutta nähdä sivua", category="error")
        return redirect("/error")
    if user_is_employee(id):
        flash("Käyttäjäsivua ei ole olemassa.", category="error")
        return redirect("/error")
    query = "SELECT A.id, A.full_name, A.street_address, A.zip_code, A.city, A.phone_number, A.email, A.visible FROM users U, addresses A WHERE U.id=A.user_id AND U.id=:id ORDER BY visible DESC"
    addresses = db.session.execute(query, {"id": id}).fetchall()
    return render_template("account.html", employee=is_employee(), id=id, username=get_username_by_user_id(id), addresses=addresses)

@app.route("/new-address/<int:id>", methods=["GET", "POST"])
def new_address(id):
    if request.method == "GET":
        if not is_logged_in():
            flash("Sinulla ei ole oikeutta nähdä sivua", category="error")
            return redirect("/error")
        return render_template("new_address.html", id=id, employee=is_employee())
    if request.method == "POST":
        full_name = request.form["full_name"]
        street_address = request.form["street_address"]
        zip_code = request.form["zip_code"]
        city = request.form["city"].upper()
        phone_number = request.form["phone_number"]
        email = request.form["email"]
        query = "INSERT INTO addresses (user_id, full_name, street_address, zip_code, city, phone_number, email) VALUES (:user_id, :full_name, :street_address, :zip_code, :city, :phone_number, :email)"
        db.session.execute(query, {"user_id": id, "full_name": full_name, "street_address": street_address, "zip_code": zip_code, "city": city, "phone_number": phone_number, "email": email})
        db.session.commit()
        flash("Uusi osoite lisätty!", category="success")
        return redirect(url_for("account", id=id))

@app.route("/edit-address/<int:id>", methods=["GET", "POST"])
def edit_address(id):
    if request.method == "GET":
        if not is_logged_in():
            flash("Sinulla ei ole oikeutta nähdä sivua", category="error")
            return redirect("/error")
        query = "SELECT user_id AS address_owner, full_name, street_address, zip_code, city, phone_number, email FROM addresses WHERE id=:id"
        address = db.session.execute(query, {"id": id}).fetchone()
        return render_template("edit_address.html", id=id, address=address, employee=is_employee())
    if request.method == "POST":
        full_name = request.form["full_name"]
        street_address = request.form["street_address"]
        zip_code = request.form["zip_code"]
        city = request.form["city"].upper()
        phone_number = request.form["phone_number"]
        email = request.form["email"]
        address_owner = request.form["address_owner"]
        query = "INSERT INTO addresses (user_id, full_name, street_address, zip_code, city, phone_number, email) VALUES (:user_id, :full_name, :street_address, :zip_code, :city, :phone_number, :email)"
        db.session.execute(query, {"user_id": address_owner, "full_name": full_name, "street_address": street_address, "zip_code": zip_code, "city": city, "phone_number": phone_number, "email": email})
        query = "UPDATE addresses SET visible=FALSE WHERE id=:id"
        db.session.execute(query, {"id": id})
        db.session.commit()
        flash("Osoitetiedot päivitetty!", category="success")
        return redirect(url_for("account", id=address_owner))

@app.route("/delete-address/<int:id>")
def delete_address(id):
    if not is_logged_in():
        flash("Sinulla ei ole oikeutta nähdä sivua", category="error")
        return redirect("/error")
    try:
        query = "SELECT user_id FROM addresses WHERE id=:id"
        address_owner = db.session.execute(query, {"id": id}).fetchone()[0]
    except TypeError:
        flash("Osoitetta ei löytynyt", category="error")
        return redirect("/error") 
    if address_owner != get_current_users_id() and not is_employee():
        flash("Sinulla ei ole oikeutta nähdä sivua", category="error")
        return redirect("/error")
    query = "UPDATE addresses SET visible=FALSE WHERE id=:id"
    db.session.execute(query, {"id": id})
    db.session.commit()
    return redirect(url_for("account", id=address_owner))

@app.route("/customers")
def customers():
    if not is_employee():
        flash("Sinulla ei ole oikeutta nähdä sivua", category="error")
        return redirect("/error")
    query = "SELECT id, username FROM users WHERE role='customer' ORDER BY username"
    customers = db.session.execute(query).fetchall()
    return render_template("customers.html", employee=is_employee(), customers=customers)

@app.route("/make-admin/<int:id>")
def make_admin(id):
    if not is_employee():
        flash("Sinulla ei ole oikeutta nähdä sivua", category="error")
        return redirect("/error")
    query = "UPDATE users SET role='employee' WHERE id=:id"
    db.session.execute(query, {"id": id})
    db.session.commit()
    flash(f"Työntekijän oikeudet lisätty käyttäjälle {get_username_by_user_id(id)}!")
    return redirect(url_for("customers"))

@app.route("/error")
def error():
    return render_template("error.html")