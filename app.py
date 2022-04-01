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
        return render_template("index.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        query = "SELECT password FROM users WHERE username=:username"
        result = db.session.execute(query, {"username": username})
        user = result.fetchone()
        if not user:
            flash("Käyttäjää ei löytynyt", category="error")
            return render_template("index.html")
        if check_password_hash(user.password, password):
            session["username"] = username
            return render_template("index.html")
        flash("Väärä salasana", category="error")
        return render_template("index.html")
        
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
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

@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")

@app.route("/new-product", methods=["GET", "POST"])
def new_product():
    if request.method == "GET":
        if is_employee():
            return(render_template("new_product.html"))
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
            return render_template("new_product.html")
        
        query = "INSERT INTO products (name, description, price, quantity) VALUES (:name, :description, :price, :quantity) RETURNING id"
        result = db.session.execute(query, {"name": name, "description": description, "price": price, "quantity": quantity})
        id = result.fetchone()[0]
        db.session.commit()
        flash("Tuote lisätty!", category="success")
        return redirect(url_for("product", id=id))

@app.route("/all-products", methods=["GET", "POST"])
def all_products():
    options = {
        "price-desc": "ORDER BY price DESC",
        "price-asc": "ORDER BY price",
        "alpha-asc": "ORDER BY name",
        "alpha-desc": "ORDER BY name DESC"
    }
    if request.method == "GET":
        try:
            username = session["username"]
        except KeyError:
            flash("Sinulla ei ole oikeutta nähdä sivua", category="error")
            return redirect("/error")
        order = "alpha-asc"
    if request.method == "POST":
        order = request.form["order"]
    query = f"SELECT id, name, description, price, quantity FROM products {options[order]}"
    result = db.session.execute(query)
    products = result.fetchall()
    return render_template("all_products.html", products=products)

@app.route("/product/<int:id>")
def product(id):
    try:
        username = session["username"]
    except KeyError:
        flash("Sinulla ei ole oikeutta nähdä sivua", category="error")
        return redirect("/error")
    query = "SELECT name, description, CAST (price AS TEXT) AS price, quantity FROM products WHERE id=:id"
    result = db.session.execute(query, {"id": id})
    product = result.fetchone()
    return render_template("product.html", id=id, product=product, role=is_employee())

@app.route("/edit-product/<int:id>", methods=["GET", "POST"])
def edit_product(id):
    if request.method == "GET":
        if not is_employee():
            flash("Sinulla ei ole oikeutta nähdä sivua", category="error")
            return redirect("/error")
        query = "SELECT name, description, CAST (price AS TEXT) AS price, quantity FROM products WHERE id=:id"
        result = db.session.execute(query, {"id": id})
        product = result.fetchone()
        return render_template("edit_product.html", id=id, product=product)
    if request.method == "POST":
        name = request.form["name"]
        quantity = request.form["quantity"]
        price = request.form["price"]
        description = request.form["description"]
        query = "UPDATE products SET name=:name, quantity=:quantity, price=:price, description=:description WHERE id=:id"
        db.session.execute(query, {"name": name, "quantity": quantity, "price": price, "description": description, "id": id})
        db.session.commit()
        flash("Tuotteen tiedot päivitetty!", category="success")
        return redirect(url_for("product", id=id))

@app.route("/error")
def error():
    return render_template("error.html")