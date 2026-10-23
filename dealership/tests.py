import json
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import Dealer, Review, CarMake, CarModel
from .views import classify_sentiment

class DriveWiseTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='student', password='SecurePass2026!')
        cls.dealer = Dealer.objects.create(name='Test Auto', address='1 Test Rd', city='Wichita', state='KS', zipcode='67201')
        cls.co_dealer = Dealer.objects.create(name='Colorado Auto', address='2 Test Rd', city='Denver', state='CO', zipcode='80201')
        cls.make = CarMake.objects.create(name='Toyota')
        CarModel.objects.create(make=cls.make, name='Camry')

    def test_home_and_details(self):
        self.assertContains(self.client.get('/'), 'Test Auto')
        self.assertContains(self.client.get(f'/dealers/{self.dealer.id}/'), 'Wichita')
        self.assertContains(self.client.get('/?state=KS'), 'Test Auto')
        self.assertNotContains(self.client.get('/?state=KS'), 'Colorado Auto')

    def test_dealer_endpoints(self):
        res = self.client.get('/api/dealerships/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.json()['dealerships']), 2)
        res = self.client.get('/api/dealerships/state/KS/')
        self.assertEqual(len(res.json()['dealerships']), 1)
        res = self.client.get(f'/api/dealerships/{self.dealer.id}/')
        self.assertEqual(res.json()['city'], 'Wichita')
        self.assertEqual(self.client.get(f'/api/reviews/dealer/{self.dealer.id}/').json()['reviews'], [])

    def test_car_makes(self):
        response = self.client.get('/api/car-makes/')
        self.assertEqual(response.json()['car_makes'][0]['models'][0]['name'], 'Camry')

    def test_authentication_and_review(self):
        self.assertEqual(self.client.post('/api/reviews/', data='{}', content_type='application/json').status_code, 401)
        logged = self.client.post('/api/auth/login/', data=json.dumps({'username': 'student', 'password': 'SecurePass2026!'}), content_type='application/json')
        self.assertEqual(logged.status_code, 200)
        payload = {'dealer_id': self.dealer.id, 'rating': 5, 'review': 'Fantastic services and staff!'}
        created = self.client.post('/api/reviews/', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(created.status_code, 201)
        self.assertEqual(Review.objects.count(), 1)
        self.assertEqual(self.client.get(f'/api/reviews/dealer/{self.dealer.id}/').json()['reviews'][0]['rating'], 5)
        self.assertEqual(self.client.post('/api/auth/logout/').status_code, 200)
        self.assertFalse(self.client.get('/api/auth/me/').json()['authenticated'])

    def test_register_validation(self):
        data = {'username': 'newperson', 'first_name': 'Test', 'last_name': 'Person', 'email': 'person@example.test', 'password': 'S3cureComplexPass!'}
        response = self.client.post('/api/auth/register/', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201, response.content)
        self.assertTrue(get_user_model().objects.filter(username='newperson').exists())
        self.assertEqual(self.client.post('/api/auth/register/', data=json.dumps(data), content_type='application/json').status_code, 400)

    def test_sentiment(self):
        self.assertEqual(classify_sentiment('Fantastic services'), 'positive')
        self.assertEqual(classify_sentiment('Awful experience'), 'negative')
        response = self.client.get('/api/sentiment/?text=Fantastic%20services')
        self.assertEqual(response.json()['sentiment'], 'positive')

    def test_csrf_protection_when_enabled(self):
        from django.test import Client
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)
        payload = {'dealer_id': self.dealer.id, 'rating': 5, 'review': 'Nice and friendly staff'}
        forbidden = client.post('/api/reviews/', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(forbidden.status_code, 403)
        csrf = client.get('/api/auth/csrf/').json()['csrfToken']
        authorized = client.post('/api/reviews/', data=json.dumps(payload), content_type='application/json', HTTP_X_CSRFTOKEN=csrf)
        self.assertEqual(authorized.status_code, 201)

    def test_static_pages_and_missing_dealer(self):
        self.assertEqual(self.client.get('/about/').status_code, 302)
        self.assertEqual(self.client.get('/contact/').status_code, 302)
        self.assertEqual(self.client.get('/api/dealerships/99999/').status_code, 404)
