import re

from flask import flash

from db import db

def get_all_addresses(id):
    query = "SELECT A.id, A.full_name, A.street_address, A.zip_code, A.city, A.phone_number, " \
            "A.email, A.visible FROM users U, addresses A WHERE U.id=A.user_id AND U.id=:id " \
            "ORDER BY visible DESC"
    addresses = db.session.execute(query, {"id": id}).fetchall()
    return addresses

def get_formatted_visible_addresses(addresses):
    user_addresses = []
    for address in addresses:
        if address[7]:
            user_addresses.append(
                (address[0], f"{address[1]}, {address[2]}, {address[3]} " \
                    f"{address[4]}, {address[5]}, {address[6]}"))
    return user_addresses

def is_visible(id):
    query = "SELECT visible FROM addresses WHERE id=:id"
    visible = db.session.execute(query, {"id": id}).fetchone()
    return visible[0] if visible else False

def new_address(id, full_name, street_address, zip_code, city, phone_number, email):
    errors = validate_user_data(
        full_name, street_address, zip_code, city, phone_number.replace(" ", ""), email)
    if errors:
        return False

    query = "INSERT INTO addresses (user_id, full_name, street_address, zip_code, city, " \
            "phone_number, email) VALUES (:user_id, :full_name, :street_address, :zip_code, " \
            ":city, :phone_number, :email)"
    db.session.execute(query, {"user_id": id, "full_name": full_name,
                               "street_address": street_address, "zip_code": zip_code,
                               "city": city, "phone_number": phone_number.replace(" ", ""),
                               "email": email})
    db.session.commit()
    return True

def get_address(id):
    query = "SELECT user_id AS address_owner, full_name, street_address, " \
            "zip_code, city, phone_number, email FROM addresses WHERE id=:id"
    address = db.session.execute(query, {"id": id}).fetchone()
    return address

def get_address_owner(id):
    query = "SELECT user_id FROM addresses WHERE id=:id"
    address_owner = db.session.execute(query, {"id": id}).fetchone()
    return address_owner[0] if address_owner else None

def delete_address(id):
    query = "UPDATE addresses SET visible=FALSE WHERE id=:id"
    db.session.execute(query, {"id": id})
    db.session.commit()

def validate_user_data(full_name, street_address, zip_code, city, phone_number, email):
    errors = False

    if not 4 < len(full_name) < 101:
        flash("Nimen tulee olla 5–100 merkkiä pitkä", category="error")
        errors = True

    if not 4 < len(street_address) < 101:
        flash("Osoitteen tulee olla 5–100 merkkiä pitkä", category="error")
        errors = True

    if not re.match("^\d{5}$", zip_code):
        flash("Virheellinen postinumero", category="error")
        errors = True

    if not 1 < len(city) < 51:
        flash("Postitoimipaikan tulee olla 2–50 merkkiä pitkä", category="error")
        errors = True

    if not re.match("^(\+?)\d{7,15}$", phone_number):
        flash("Virheellinen puhelinnumero", category="error")
        errors = True

    if not re.match("^\S+@\S+\.\S+$", email) or not 4 < len(email) < 320:
        flash("Virheellinen sähköpostiosoite", category="error")
        errors = True

    return errors
