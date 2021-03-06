import re

from flask import flash, session
import secrets
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
    session["csrf_token"] = secrets.token_hex(16)
    return True

def login(username, password):
    query = "SELECT password FROM users WHERE username=:username"
    user = db.session.execute(query, {"username": username}).fetchone()
    if not user:
        flash("Käyttäjää ei löytynyt", category="error")
        return False
    if check_password_hash(user.password, password):
        session["username"] = username
        session["csrf_token"] = secrets.token_hex(16)
        return True
    flash("Väärä salasana", category="error")
    return False

def user_exists(user_id):
    query = "SELECT 1 FROM users WHERE id=:user_id"
    result = db.session.execute(query, {"user_id": user_id})
    return True if result.fetchone() else False

def logout():
    del session["username"]

def is_employee(user_id=None):
    if not user_id:
        user_id = get_user_id_by_username()
    query = "SELECT role FROM users WHERE id=:user_id"
    role = db.session.execute(query, {"user_id": user_id}).fetchone()
    if not role or role[0] != "employee":
        return False
    return True

def is_logged_in():
    return session.get("username")

def get_user_id_by_username(username=None):
    username = session.get("username") if not username else username
    query = "SELECT id FROM users WHERE username=:username"
    user_id = db.session.execute(query, {"username": username}).fetchone()
    return user_id[0] if user_id else None

def get_username_by_user_id(user_id):
    query = "SELECT username FROM users WHERE id=:user_id"
    username = db.session.execute(query, {"user_id": user_id}).fetchone()
    return username[0] if username else None

def get_all_customers():
    query = "SELECT id, username FROM users WHERE role='customer' ORDER BY username"
    customers = db.session.execute(query).fetchall()
    return customers

def make_admin(id):
    query = "UPDATE users SET role='employee' WHERE id=:id"
    db.session.execute(query, {"id": id})
    db.session.commit()
