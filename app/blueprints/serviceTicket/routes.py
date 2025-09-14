from __future__ import annotations
from datetime import datetime
from flask import request, jsonify
from sqlalchemy import select
from marshmallow import ValidationError
from .schemas import serviceTicket_schema, serviceTickets_schema
from app.models import ServiceTickets, Mechanics, Inventory, InventoryServiceTicket, db
from flask import Blueprint
from app.utils.util import token_required

serviceTickets_bp = Blueprint('serviceTickets_bp', __name__, url_prefix="/serviceTickets")

#   ServiceTickets
#	GET /serviceTickets: Retrieve service ticket by id
@serviceTickets_bp.route('/<int:id>', methods=['GET'])
def get_Service_Ticket(id):
    serviceTicket = db.session.get(ServiceTickets, id)
    return serviceTicket_schema.jsonify(serviceTicket), 200

#	GET /serviceTickets: Retrieve all serviceTickets
@serviceTickets_bp.route('/', methods=['GET'])
def get_serviceTickets():
    query = select(ServiceTickets)
    serviceTickets = db.session.execute(query).scalars().all()
    return serviceTickets_schema.jsonify(serviceTickets), 200

#	GET /serviceTickets/mytickets: Retrieve all tickets by user id provided in token
@serviceTickets_bp.route('/mytickets', methods=['GET'])
@token_required
def get_mytickets(user_id): #Recieving user_id from the token
    query = select(ServiceTickets).where(ServiceTickets.customer_id == user_id)
    serviceTickets = db.session.execute(query).scalars().all()
    return serviceTickets_schema.jsonify(serviceTickets), 200

# #  POST /serviceTickets: Create a new service ticket
# @serviceTickets_bp.route('/', methods=['POST'])
# def create_serviceTicket():
#     try:
#     # serviceTicket_data = serviceTicket_schema.load(request.json)
#         newServiceTicket = serviceTicket_schema.load(request.json, session=db.session)
#     except ValidationError as e:
#         return jsonify(e.messages), 400
#     # NewServiceTicket = ServiceTickets(VIN=serviceTicket_data['VIN'], service_date=serviceTicket_data['service_date'], service_desc=serviceTicket_data['service_desc'],customer_id=serviceTicket_data['customer_id'])
#     # newServiceTicket = ServiceTickets(**serviceTicket_data)

#     db.session.add(newServiceTicket)
#     db.session.commit()

#     return serviceTicket_schema.jsonify(newServiceTicket), 201

@serviceTickets_bp.route("/", methods=["POST"])
def create_serviceTicket():
    try:
        serviceTicket_data = request.get_json()  # or schema.load()
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    service_date = serviceTicket_data.get("service_date")
    if isinstance(service_date, str):
        try:
            service_date = datetime.strptime(service_date, "%Y-%m-%d").date()
        except ValueError:
            return {"error": "Invalid date format, expected YYYY-MM-DD"}, 400

    # Make sure this is a model instance, not a dict
    newServiceTicket = ServiceTickets(
        VIN=serviceTicket_data["VIN"],
        service_date=service_date,
        service_desc=serviceTicket_data["service_desc"],
        customer_id=serviceTicket_data["customer_id"],
    )

    db.session.add(newServiceTicket)
    db.session.commit()

    return jsonify({"message": "Service ticket created", "id": newServiceTicket.id}), 201

#	PUT /serviceTickets/<id>: Update a service ticket by ID
@serviceTickets_bp.route('/<int:id>', methods=['PUT'])
def updateServiceTicket(id):
    serviceTicket = db.session.get(ServiceTickets, id)

    if not serviceTicket:
        return jsonify({"message": "Invalid service ticket id"}), 400
    
    try:
        serviceTicket_data = serviceTicket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    serviceTicket.VIN = serviceTicket_data['VIN']
    serviceTicket.service_date = serviceTicket_data['service_date']
    serviceTicket.service_desc = serviceTicket_data['service_desc']

    db.session.commit()
    return serviceTicket_schema.jsonify(serviceTicket), 200


@serviceTickets_bp.route("/<int:ticket_id>/edit", methods=["PUT"])
def update_ticket_mechanics(ticket_id):
    try:
        ticket_data = request.json
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    add_ids = ticket_data.get("add_ids", [])
    remove_ids = ticket_data.get("remove_ids", [])

    query = select(ServiceTickets).where(ServiceTickets.id == ticket_id)
    ticket = db.session.execute(query).scalars().first()
    if not ticket:
        return jsonify({"error": "Ticket not found"}), 404

    # Remove mechanics
    for mechId in remove_ids:
        mechanic = db.session.get(Mechanics, mechId)
        if mechanic in ticket.mechanics:
            ticket.mechanics.remove(mechanic)

    # Add mechanics
    for mechId in add_ids:
        mechanic = db.session.get(Mechanics, mechId)
        if mechanic not in ticket.mechanics:
            ticket.mechanics.append(mechanic)

    db.session.commit()

    return jsonify({"success": "Ticket assigned"}), 200



#  DELETE /serviceTickets/<id>: Delete a service ticket by ID
@serviceTickets_bp.route('/<int:id>', methods=['DELETE'])
def delete_serviceTicket(id):
    serviceTicket = db.session.get(ServiceTickets, id)

    if not serviceTicket:
        return jsonify({"message": "Invalid service ticket id"}), 400
    db.session.delete(serviceTicket)
    db.session.commit()
    return jsonify({"message": f"succefully deleted service ticket {id}"}), 200



@serviceTickets_bp.route("/<int:ticket_id>/add_part", methods=["POST"])
def add_part_to_service_ticket(ticket_id):
    data = request.get_json()

    inventory_id = data.get("inventory_id")
    quantity = data.get("quantity", 1)

    # Ensure the Service Ticket exists
    service_ticket = db.session.get(ServiceTickets, ticket_id)
    if not service_ticket:
        return jsonify({"error": "Service Ticket not found"}), 404

    # Ensure the Inventory item exists
    inventory = db.session.get(Inventory, inventory_id)
    if not inventory:
        return jsonify({"error": "Inventory item not found"}), 404

    # Create link row in InventoryServiceTicket
    link = InventoryServiceTicket(
        inventory_id=inventory_id,
        service_ticket_id=ticket_id,
        quantity=quantity,
    )

    db.session.add(link)
    db.session.commit()

    return jsonify({
        "message": "Part added successfully",
        "ticket_id": ticket_id,
        "inventory_id": inventory_id,
        "quantity": quantity
    }), 201
