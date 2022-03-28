from os import getenv

from flask import Flask
from flask import flash, redirect, render_template, request, session
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
        username = request.form["username"]
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        if len(password1) < 5:
            flash("Salasanassa tulee olla vähintään viisi merkkiä", category="error")
            return render_template("register.html")
        if password1 != password2:
            flash("Salasanat eivät täsmää", category="error")
            return render_template("register.html")
        query = "SELECT COUNT(*) FROM users WHERE LOWER(username)=:username"
        result = db.session.execute(query, {"username": username.lower()})
        user_count = result.fetchone()[0]
        if user_count != 0:
            flash("Käyttäjätunnus on jo käytössä", category="error")
            return render_template("register.html")
        query = "INSERT INTO users (username, password, role) VALUES (:username, :password, 'customer')"
        db.session.execute(query, {"username": username, "password": generate_password_hash(password1)})
        db.session.commit()
        session["username"] = username
        return redirect("/")

@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")

@app.route("/new-product", methods=["GET", "POST"])
def add_product():
    if request.method == "GET":
        try:
            username = session["username"]
        except KeyError:
            flash("Sinulla ei ole oikeutta nähdä sivua", category="error")
            return redirect("/error")
        query = "SELECT role FROM users WHERE username=:username"
        result = db.session.execute(query, {"username": username})
        role = result.fetchone()[0]
        if role == "employee":
            return(render_template("new_product.html"))
        flash("Sinulla ei ole oikeutta nähdä sivua", category="error")
        return redirect("/error")
    if request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]

        if not name.strip():
            flash("Syötä tuotteen nimi", category="error")
            return render_template("new_product.html")
        try:
            quantity = int(request.form["quantity"])
        except ValueError:
            flash("Syötä varastosaldo", category="error")
            return render_template("new_product.html")
        try:
            price = float(request.form["price"])
        except ValueError:
            flash("Syötä hinta", category="error")
            return render_template("new_product.html")
        
        query = "INSERT INTO products (name, description, price, quantity) VALUES (:name, :description, :price, :quantity)"
        db.session.execute(query, {"name": name, "description": description, "price": price, "quantity": quantity})
        db.session.commit()
        flash(f"Tuote {name} lisätty!", category="success")
        return render_template("new_product.html")
        
@app.route("/error")
def error():
    return render_template("error.html")