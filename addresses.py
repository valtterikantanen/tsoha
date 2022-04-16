from db import db

def get_all_addresses(id):
    query = "SELECT A.id, A.full_name, A.street_address, A.zip_code, A.city, A.phone_number, A.email, A.visible FROM users U, addresses A WHERE U.id=A.user_id AND U.id=:id ORDER BY visible DESC"
    addresses = db.session.execute(query, {"id": id}).fetchall()
    return addresses

def new_address(id, full_name, street_address, zip_code, city, phone_number, email):
    query = "INSERT INTO addresses (user_id, full_name, street_address, zip_code, city, phone_number, email) VALUES (:user_id, :full_name, :street_address, :zip_code, :city, :phone_number, :email)"
    db.session.execute(query, {"user_id": id, "full_name": full_name, "street_address": street_address, "zip_code": zip_code, "city": city, "phone_number": phone_number, "email": email})
    db.session.commit()

def get_address(id):
    query = "SELECT user_id AS address_owner, full_name, street_address, zip_code, city, phone_number, email FROM addresses WHERE id=:id"
    address = db.session.execute(query, {"id": id}).fetchone()
    return address

def get_address_owner(id):
    try:
        query = "SELECT user_id FROM addresses WHERE id=:id"
        address_owner = db.session.execute(query, {"id": id}).fetchone()[0]
        return address_owner
    except TypeError:
        return False

def delete_address(id):
    query = "UPDATE addresses SET visible=FALSE WHERE id=:id"
    db.session.execute(query, {"id": id})
    db.session.commit()