from flask import flash, redirect, render_template, request, url_for

from app import app
from db import db
import addresses
import products
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
        name = request.form["name"]
        description = request.form["description"]
        quantity = request.form["quantity"]
        price = request.form["price"]
        product_id = products.add_product(name, description, quantity, price)
        if not product_id:
            return render_template("new_product.html", employee=users.is_employee())
        return redirect(url_for("product", id=product_id))

@app.route("/all-products", methods=["GET", "POST"])
def all_products():
    if not users.is_logged_in():
        flash("Sinulla ei ole oikeutta nähdä sivua", category="error")
        return redirect("/error")
    order = request.form["order"] if request.method == "POST" else "alpha-asc"
    return render_template("all_products.html", products=products.all_products(order), id=users.get_user_id_by_username(), employee=users.is_employee())

@app.route("/product/<int:id>")
def product(id):
    if not users.is_logged_in():
        flash("Sinulla ei ole oikeutta nähdä sivua", category="error")
        return redirect("/error")
    return render_template("product.html", id=id, product=products.get_product_info(id), price_history=products.get_price_history(id), employee=users.is_employee())

@app.route("/edit-product/<int:id>", methods=["GET", "POST"])
def edit_product(id):
    if request.method == "GET":
        if not users.is_employee():
            flash("Sinulla ei ole oikeutta nähdä sivua", category="error")
            return redirect("/error")
        return render_template("edit_product.html", id=id, product=products.get_product_info(id), employee=users.is_employee())
    if request.method == "POST":
        name = request.form["name"]
        quantity = request.form["quantity"]
        price = request.form["price"]
        description = request.form["description"]
        products.edit_product(id, name, quantity, price, description)
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