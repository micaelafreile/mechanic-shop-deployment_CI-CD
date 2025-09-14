
from app.extensions import ma
from app.models import InventoryServiceTicket, Inventory, ServiceTickets, db
from marshmallow_sqlalchemy.fields import Nested

class InventoryServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = InventoryServiceTicket
        load_instance = True
        include_fk = True
        sqla_session = db.session

    # Relationships
    service_ticket = Nested("ServiceTicketSchema", exclude=("inventory_tickets",))
    inventory = Nested("InventorySchema", exclude=("inventory_tickets",))  # prevents circular nesting


class InventorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Inventory
        load_instance = True
        sqla_session = db.session

    # Include related tickets
    inventory_tickets = Nested(InventoryServiceTicketSchema, many=True, exclude=("inventory",))


class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ServiceTickets
        load_instance = True
        sqla_session = db.session

    # Show inventory tickets, but exclude service_ticket itself to avoid recursion
    inventory_tickets = Nested(InventoryServiceTicketSchema, many=True, exclude=("service_ticket",))
