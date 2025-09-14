
from app import create_app
from app.models import db, Mechanics, ServiceMechanics, ServiceTickets, Customers
from datetime import date
import unittest

class TestMechanics(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        self.client = self.app.test_client()
        with self.app.app_context():
            db.drop_all()
            db.create_all()

    
    def test_create_mechanic(self):
        mechanic_payload = {
            "name": "Jane Doe",
            "email": "jd@email.com",
            "phone": "555-555-5555",
            "salary": "50"
        }

        response = self.client.post('/mechanics/', json=mechanic_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['name'], "Jane Doe")

    
    def test_get_all_mechanics(self):
        with self.app.app_context():
            # Arrange: add a mechanic
            mechanic = Mechanics(name="Jack",email="jack@aol.com",phone="333-333-3333", salary= 10)
            db.session.add(mechanic)
            db.session.commit()

        response = self.client.get('/mechanics/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json[0]['name'], "Jack")      

    
    def test_invalid_creation(self):
        mechanic_payload = {
            "name": "John Doe",
            "email": "jd@email.com", #fails already existing email address
            "phone": "555-555-5555",
            "salary": "10"
        }

        response = self.client.post('/mechanics/', json=mechanic_payload)
        self.assertEqual(response.status_code, 201)


    def test_invalid_payload(self):
        mechanic_payload = {} # Invalid payload

        response = self.client.post('/mechanics/', json=mechanic_payload)
        self.assertEqual(response.status_code, 400)


    def test_delete_mechanic_success(self):
        with self.app.app_context():
            # Arrange: add a mechanic
            mechanic = Mechanics(name="Jack",email="jack@aol.com",phone="333-333-3333", salary= 10)
            db.session.add(mechanic)
            db.session.commit()
            mechanic_id = mechanic.id

        # Act: call DELETE
        response = self.client.delete(f"/mechanics/{mechanic_id}")

        # Assert: check response
        self.assertEqual(response.status_code, 200)
        self.assertIn(f"succefully deleted mechanic {mechanic_id}", response.json["message"])

        # Assert: check DB no longer has the mechanic
        with self.app.app_context():
            deleted = db.session.get(Mechanics, mechanic_id)
            self.assertIsNone(deleted)

    def test_mechanics_ticket_count(self):
        with self.app.app_context():
            # Arrange: create mechanics
            jack = Mechanics(
                name="Jack",
                email="jack@example.com",
                phone="111-111-1111",
                salary=50000
            )
            tom = Mechanics(
                name="Tom",
                email="tom@example.com",
                phone="222-222-2222",
                salary=45000
)
            db.session.add_all([jack, tom])
            db.session.commit()

            # Arrange: create customer
            c1 = Customers(name = "John Doe", email= "jd@email.com", phone= "555-555-5555",password= "123")
            db.session.add(c1)
            db.session.commit()

            # Arrange: create service tickets
            t1 = ServiceTickets(VIN="1HGCM82633A123456",service_date=date(2025, 9, 12),service_desc="Oil change",customer_id=c1.id)
            t2 = ServiceTickets(VIN="1HGCM82633A123457",service_date=date(2025, 9, 12),service_desc="Brake check",customer_id=c1.id)
            t3= ServiceTickets(VIN="1HGCM82633A123458",service_date=date(2025, 9, 12),service_desc="Engine repair",customer_id=c1.id)
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