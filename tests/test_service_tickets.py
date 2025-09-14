
from datetime import date, datetime
from app import create_app
from app.models import ServiceTickets, Mechanics, Inventory, InventoryServiceTicket, Customers, db
from app.utils.util import encode_token
import unittest

class TestServiceTicket(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            self.customer = Customers(name="test_user", email="test@email.com", phone="555-555-5555" , password="test")
            db.session.add(self.customer)
            db.session.commit()
        self.token = encode_token(1)            
        self.client = self.app.test_client()

    def test_create_serviceticket(self):
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            self.customer = Customers(name="test_user", email="test@email.com", phone="555-555-5555" , password="test")
            db.session.add(self.customer)
            db.session.commit()            

            # Act: call endpoint
            serviceticket_payload = {
                "VIN": "1HGCM82633A123456",
                "service_desc": "brakes",
                "service_date": "2025-09-12",
                "customer_id": self.customer.id
            }
            
            response = self.client.post("/serviceTickets/", json=serviceticket_payload)

            # Assert
            self.assertEqual(response.status_code, 201)
            self.assertIn(f"Service ticket created", response.json["message"])     


    def test_get_all_servicetickets(self):
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            self.customer = Customers(name="test_user", email="test@email.com", phone="555-555-5555" , password="test")
            db.session.add(self.customer)
            db.session.commit()       

            # Arrange: add a serviceticket
            service_ticket = ServiceTickets(
                VIN = "1HGCM82633A123456", 
                service_desc = "brakes", 
                service_date = date(2025, 9, 12), 
                customer_id = self.customer.id)
            db.session.add(service_ticket)
            db.session.commit()
            
            response = self.client.get('/serviceTickets/')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json[0]['VIN'], '1HGCM82633A123456')

    def test_get_my_tickets(self):
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            self.customer = Customers(name="test_user", email="test@email.com", phone="555-555-5555" , password="test")
            db.session.add(self.customer)
            db.session.commit()       

            # Arrange: add a serviceticket
            service_ticket = ServiceTickets(
                VIN = "1HGCM82633A123456", 
                service_desc = "brakes", 
                service_date = date(2025, 9, 12), 
                customer_id = self.customer.id)
            db.session.add(service_ticket)
            db.session.commit()
            
            headers = {'Authorization': "Bearer " + self.test_login_customer()}
            response = self.client.get('/serviceTickets/mytickets', headers=headers)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json[0]['VIN'], '1HGCM82633A123456')            
 
 
    def test_login_customer(self):
        # See line 13 above:   self.customer = Customers(... 
        credentials = {
            "email": "test@email.com",
            "password": "test"
        }

        response = self.client.post('/customers/login', json=credentials)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], 'success')
        return response.json['auth_token']


    def test_delete_service_ticket_success(self):

        with self.app.app_context():
            db.drop_all()
            db.create_all()
            self.customer = Customers(name="test_user", email="test@email.com", phone="555-555-5555" , password="test")
            db.session.add(self.customer)
            db.session.commit()       

            # Arrange: add a serviceticket
            service_ticket = ServiceTickets(
                VIN = "1HGCM82633A123456", 
                service_desc = "brakes", 
                service_date = date(2025, 9, 12), 
                customer_id = self.customer.id)
            db.session.add(service_ticket)
            db.session.commit()
            service_ticket_id = service_ticket.id

        # Act: call DELETE
        response = self.client.delete(f"/serviceTickets/{service_ticket_id}")

        # Assert: check response
        self.assertEqual(response.status_code, 200)
        self.assertIn(f"succefully deleted service ticket {service_ticket_id}", response.json["message"])

        # Assert: check DB no longer has the serviceticket
        with self.app.app_context():
            deleted = db.session.get(ServiceTickets, service_ticket_id)
            self.assertIsNone(deleted)