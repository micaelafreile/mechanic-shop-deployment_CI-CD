from __future__ import annotations
from flask import request, jsonify
from sqlalchemy import func, select
from marshmallow import ValidationError
from .schemas import customer_schema, customers_schema
from app.models import Customers, db
from flask import Blueprint
from app.utils.util import encode_token, token_required
# from app.extensions import limiter

customers_bp = Blueprint('customers', __name__, url_prefix="/customers")

@customers_bp.route("/login", methods=['POST'])
def login():
    try:
        credentials = request.json
        username = credentials['email']
        password = credentials['password']
    except KeyError:
        return jsonify({'messages': 'Invalid payload, expecting username and password'}), 400
  
    query =select(Customers).where(Customers.email == username)
    user = db.session.execute(query).scalar_one_or_none() #Query user table for a user with this email

    if user and user.password == password: #if we have a user associated with the username, validate the password
        #auth_token = encode_token(user.id, user.role.role_name)
        auth_token = encode_token(user.id)

        response = {
            "status": "success",
            "message": "Successfully Logged In",
            "auth_token": auth_token
        }
        return jsonify(response), 200
    else:
        return jsonify({'messages': "Invalid email or password"}), 401

#   Customers
#	GET /customers: Retrieve customer by id
@customers_bp.route('/<int:id>', methods=['GET'])
def get_customer(id):
    customer = db.session.get(Customers, id)
    return customer_schema.jsonify(customer), 200

#	GET /customers: Retrieve all customers
@customers_bp.route('/', methods=['GET'])
def get_customers():
    query = select(Customers)
    customers = db.session.execute(query).scalars().all()
    return customers_schema.jsonify(customers), 200


@customers_bp.route('/byPage', methods=['GET'])
def get_customers_by_page():
    page = int(request.args.get('page'))
    per_page = int(request.args.get('per_page'))

    try:
        page = int(request.args.get('page'))
        per_page = int(request.args.get('per_page'))
        query = select(Customers)
        customers = db.paginate(query, page=page, per_page=per_page)
        return customers_schema.jsonify(customers), 200
    except:
        query = select(Customers)
        customers = db.session.execute(query).scalars().all() 
        return customers_schema.jsonify(customers), 200 

#  POST /customers: Create a new customer
@customers_bp.route('/', methods=['POST'])
def create_customer():
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_customer = Customers(name=customer_data['name'], email=customer_data['email'], phone=customer_data['phone'],password=customer_data['password'])
    db.session.add(new_customer)
    db.session.commit()

    return customer_schema.jsonify(new_customer), 201

#	PUT /customers/<id>: Update a customer by ID
@customers_bp.route('/<int:id>', methods=['PUT'])
def update_customer(id):
    customer = db.session.get(Customers, id)

    if not customer:
        return jsonify({"message": "Invalid customer id"}), 400
    
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    customer.name = customer_data['name']
    customer.email = customer_data['email']
    customer.phone = customer_data['phone']
    customer.password = customer_data['password']

    db.session.commit()
    return customer_schema.jsonify(customer), 200

#   DELETE /customers/<id>: Delete a customer by ID
# @customers_bp.route('/<int:id>', methods=['DELETE'])
# def delete_customer(id):
#     customer = db.session.get(Customers, id)

#     if not customer:
#         return jsonify({"message": "Invalid customer id"}), 400
#     db.session.delete(customer)
#     db.session.commit()
#     return jsonify({"message": f"succefully deleted customer {id}"}), 200


@customers_bp.route('/', methods=['DELETE'])
@token_required
def delete_user(user_id): #Recieving user_id from the token
    query = select(Customers).where(Customers.id == user_id)
    user = db.session.execute(query).scalars().first()
		
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": f"succesfully deleted user {user_id}"})
