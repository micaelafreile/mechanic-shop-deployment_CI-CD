from __future__ import annotations
from flask import request, jsonify
from sqlalchemy import select
from marshmallow import ValidationError
from .schemas import InventoryServiceTicketSchema, InventorySchema, ServiceTicketSchema
from app.models import Inventory, db
from flask import Blueprint
# from app.utils.util import token_required

inventory_bp = Blueprint('inventory_bp', __name__, url_prefix="/inventory")

# GET
@inventory_bp.route('/<int:id>', methods=['GET'])
def get_inventory_by_id(id):
    inventory_item = db.session.get(Inventory, id)
    return InventorySchema.jsonify(inventory_item), 200

# GET
@inventory_bp.route('/', methods=['GET'])
def get_all_inventory():
    query = select(Inventory)
    inventory_item = db.session.execute(query).scalars().all()
    return InventorySchema.jsonify(inventory_item), 200

#  POST 
@inventory_bp.route('/', methods=['POST'])
def create_Inventory():
    try:
        inventory_data = InventorySchema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_Inventory_item = Inventory(
        name=inventory_data['name'], 
        price=inventory_data['price'])
    db.session.add(new_Inventory_item)
    db.session.commit()

    return InventorySchema.jsonify(new_Inventory_item), 201

#	PUT
@inventory_bp.route('/<int:id>', methods=['PUT'])
def updateInventory(id):
    inventory_item = db.session.get(Inventory, id)

    if not inventory_item:
        return jsonify({"message": "Invalid inventory id"}), 400
    
    try:
        inventory_data = InventorySchema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    inventory_item.name = inventory_data['name']
    inventory_item.price = inventory_data['price']

    db.session.commit()
    return InventorySchema.jsonify(inventory_item), 200


#  DELETE 
@inventory_bp.route('/<int:id>', methods=['DELETE'])
def delete_Inventory(id):
    inventory_item = db.session.get(Inventory, id)

    if not inventory_item:
        return jsonify({"message": "Invalid inventory id"}), 400
    db.session.delete(inventory_item)
    db.session.commit()
    return jsonify({"message": f"succefully deleted inventory {id}"}), 200