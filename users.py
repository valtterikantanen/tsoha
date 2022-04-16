import re

from flask import flash, session
from werkzeug.security import check_password_hash, generate_password_hash

from db import db

def register(username, password1, password2):
    errors = False
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
    user_count = db.session.execute(query, {"username": username.lower()}).fetchone()[0]
    if user_count != 0:
        flash("Käyttäjätunnus on jo käytössä", category="error")
        errors = True
    if errors:
        return False
    query = "INSERT INTO users (username, password) VALUES (:username, :password)"
    db.session.execute(query, {"username": username, "password": generate_password_hash(password1)})
    db.session.commit()
    session["username"] = username
    return True

def login(username, password):
    query = "SELECT password FROM users WHERE username=:username"
    user = db.session.execute(query, {"username": username}).fetchone()
    if not user:
        flash("Käyttäjää ei löytynyt", category="error")
        return False
    if check_password_hash(user.password, password):
        session["username"] = username
        return True
    flash("Väärä salasana", category="error")
    return False

def logout():
    del session["username"]

def is_employee(user_id=None):
    if not user_id:
        user_id = get_user_id_by_username()
    try:
        query = "SELECT role FROM users WHERE id=:user_id"
        role = db.session.execute(query, {"user_id": user_id}).fetchone()[0]
        return role == "employee"
    except:
        return False

def is_logged_in():
    return session.get("username")

def get_user_id_by_username(username=None):
    if not username:
        username = session.get("username")
    try:
        query = "SELECT id FROM users WHERE username=:username"
        user_id = db.session.execute(query, {"username": username}).fetchone()[0]
        return user_id
    except TypeError:
        return False

def get_username_by_user_id(user_id):
    query = "SELECT username FROM users WHERE id=:user_id"
    username = db.session.execute(query, {"user_id": user_id}).fetchone()[0]
    return username

def get_all_customers():
    if not is_employee():
        return False
    query = "SELECT id, username FROM users WHERE role='customer' ORDER BY username"
    customers = db.session.execute(query).fetchall()
    return customers

def make_admin(id):
    if not is_employee():
        return False
    query = "UPDATE users SET role='employee' WHERE id=:id"
    db.session.execute(query, {"id": id})
    db.session.commit()
    return True