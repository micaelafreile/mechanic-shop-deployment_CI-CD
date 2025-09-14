from __future__ import annotations
from flask import request, jsonify
from sqlalchemy import desc, func, select
from marshmallow import ValidationError
from .schemas import mechanic_schema, mechanics_schema
from app.models import Mechanics, ServiceMechanics, ServiceTickets, db
from flask import Blueprint
from app.extensions import limiter, cache

mechanics_bp = Blueprint('mechanics', __name__, url_prefix="/mechanics")

@mechanics_bp.route('/<int:id>', methods=['GET'])
def get_mechanic(id):
    mechanic = db.session.get(Mechanics, id)
    return mechanic_schema.jsonify(mechanic), 200

#	GET /mechanics: Retrieve all mechanics
@mechanics_bp.route('/', methods=['GET'])
# Do not allow more that set number of requests within time period. Helps prevent unneded requests and is better for application performance.
@limiter.limit("10 per minute") 
#improve performance by going to database every 30 seconds. Instead of every time. Cahing keeps a copy of results and returns it if within the 30 secs
@cache.cached(timeout=30)  
def get_mechanics():
    query = select(Mechanics)
    mechanics = db.session.execute(query).scalars().all()
    return mechanics_schema.jsonify(mechanics), 200

@mechanics_bp.route('/byNumberOfTickets', methods=['GET'])
def get_mechanics_by_ticket_count():
    results = (
        db.session.query(
            Mechanics.id,
            Mechanics.name,
            func.count(ServiceTickets.id).label("ticket_count")
        )
        .join(ServiceMechanics, Mechanics.id == ServiceMechanics.c.mechanic_id)
        .join(ServiceTickets, ServiceTickets.id == ServiceMechanics.c.service_ticket_id)
        .group_by(Mechanics.id, Mechanics.name)
        .order_by(desc("ticket_count"))
        .all()
    )

    # Convert result tuples into dictionary
    data = [
        {"id": r.id, "name": r.name, "ticket_count": r.ticket_count}
        for r in results
    ]

    return jsonify(data), 200

#  POST /mechanics: Create a new mechanic
@mechanics_bp.route('/', methods=['POST'])
def create_mechanic():
    try:
        mechanic_data = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_mechanic = Mechanics(name=mechanic_data['name'], email=mechanic_data['email'], phone=mechanic_data['phone'], salary=mechanic_data['salary'])
    db.session.add(new_mechanic)
    db.session.commit()

    return mechanic_schema.jsonify(new_mechanic), 201

#	PUT /mechanics/<id>: Update a mechanic by ID
@mechanics_bp.route('/<int:id>', methods=['PUT'])
def update_mechanic(id):
    mechanic = db.session.get(Mechanics, id)

    if not mechanic:
        return jsonify({"message": "Invalid mechanic id"}), 400
    
    try:
        mechanic_data = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    mechanic.name = mechanic_data['name']
    mechanic.email = mechanic_data['email']
    mechanic.phone = mechanic_data['phone']
    mechanic.salary = mechanic_data['salary']

    db.session.commit()
    return mechanic_schema.jsonify(mechanic), 200

#   DELETE /mechanics/<id>: Delete a mechanic by ID
@mechanics_bp.route('/<int:id>', methods=['DELETE'])
def delete_mechanic(id):
    mechanic = db.session.get(Mechanics, id)

    if not mechanic:
        return jsonify({"message": "Invalid mechanic id"}), 400
    db.session.delete(mechanic)
    db.session.commit()
    return jsonify({"message": f"succefully deleted mechanic {id}"}), 200

def test_mechanics_ticket_count(self):
    with self.app.app_context():
        # Arrange: create mechanics
        jack = Mechanics(name="Jack")
        tom = Mechanics(name="Tom")
        db.session.add_all([jack, tom])
        db.session.commit()

        # Arrange: create service tickets
        t1 = ServiceTickets(description="Oil change")
        t2 = ServiceTickets(description="Brake check")
        t3 = ServiceTickets(description="Engine repair")
        db.session.add_all([t1, t2, t3])
        db.session.commit()

        # Assign tickets: Jack -> 2, Tom -> 1
        db.session.execute(ServiceMechanics.insert().values(service_ticket_id=t1.id, mechanic_id=jack.id))
        db.session.execute(ServiceMechanics.insert().values(service_ticket_id=t2.id, mechanic_id=jack.id))
        db.session.execute(ServiceMechanics.insert().values(service_ticket_id=t3.id, mechanic_id=tom.id))
        db.session.commit()

        # Act: call endpoint
    response = self.client.get("/mechanics/byNumberOfTickets")

    # Assert: endpoint works
    self.assertEqual(response.status_code, 200)

    data = response.get_json()
    # Ordered by ticket_count desc → Jack first, Tom second
    self.assertEqual(len(data), 2)
    self.assertEqual(data[0]["name"], "Jack")
    self.assertEqual(data[0]["ticket_count"], 2)
    self.assertEqual(data[1]["name"], "Tom")
    self.assertEqual(data[1]["ticket_count"], 1)
