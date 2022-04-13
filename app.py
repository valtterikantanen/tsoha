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
            return render_template("index.html", employee=is_employee())
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
            return render_template("index.html", employee=is_employee())
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
        result = db.session.execute(query, {"username": username})
        role = result.fetchone()[0]
        return role == "employee"
    except:
        return False

def is_logged_in():
    return session.get("username")

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
    return render_template("all_products.html", products=products, employee=is_employee())

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
        result = db.session.execute(query, {"id": id})
        product = result.fetchone()
        return render_template("edit_product.html", id=id, product=product)
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
        if current_price != price:
            query = "INSERT INTO prices (product_id, price) VALUES (:product_id, :price)"
            db.session.execute(query, {"product_id": id, "price": price})
            db.session.commit()
        flash("Tuotteen tiedot päivitetty!", category="success")
        return redirect(url_for("product", id=id))

@app.route("/error")
def error():
    return render_template("error.html")