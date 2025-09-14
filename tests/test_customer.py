
from app import create_app
from app.models import db, Customers
from app.utils.util import encode_token
import unittest

class TestCustomer(unittest.TestCase):
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


    def test_create_customer(self):
        customer_payload = {
            "name": "Jane Doe",
            "email": "jd@email.com",
            "phone": "555-555-5555",
            "password": "123"
        }

        response = self.client.post('/customers/', json=customer_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['name'], "Jane Doe")


    def test_invalid_creation(self):
        customer_payload = {
            "name": "John Doe",
            "email": "jd@email.com", #fails already existing email address
            "phone": "555-555-5555",
            "password": "123"
        }

        response = self.client.post('/customers/', json=customer_payload)
        self.assertEqual(response.status_code, 201)

    def test_invalid_payload(self):
        customer_payload = {} # Invalid payload

        response = self.client.post('/customers/', json=customer_payload)
        self.assertEqual(response.status_code, 400)


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


    def test_invalid_login(self):
        credentials = {
            "email": "bad_email@email.com",
            "password": "bad_pw"
        }

        response = self.client.post('/customers/login', json=credentials)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json['messages'], 'Invalid email or password')


    def test_get_all_customers(self):
        response = self.client.get('/customers/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json[0]['name'], 'test_user')


    def test_delete_customer(self):
        headers = {'Authorization': "Bearer " + self.test_login_customer()}
        response = self.client.delete('/customers/', headers=headers)
        self.assertEqual(response.status_code, 200)