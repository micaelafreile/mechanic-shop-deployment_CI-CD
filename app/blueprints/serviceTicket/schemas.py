
from app.extensions import ma
from app.models import ServiceTickets

# Service Tickets Schema
class ServiceTicketsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ServiceTickets

serviceTicket_schema = ServiceTicketsSchema()
serviceTickets_schema = ServiceTicketsSchema(many=True)