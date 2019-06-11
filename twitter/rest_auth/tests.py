from django.contrib.auth.hashers import make_password
from django.test import TestCase, Client
import jwt
from rest_auth.models import TwitterUser, TwitterUserToken
from django.conf import settings


class TestAuthentication(TestCase):
    user = None

    def generate_token(self):
        payload = {
            'username': self.user.username,
            'email': self.user.email,
        }
        jwt_token = jwt.encode(payload, settings.ENCRYPTION_SECRET_KEY)
        TwitterUserToken.objects.create(token=jwt_token, user=self.user)

    def setUp(self):
        client = Client()
        self.user = TwitterUser.objects.create(email='151031vaibha@gmail.com', username='tidu11313',
                                               password=make_password('14141141'), contact_number='+918010222222',
                                               first_name='vaibhav', last_name='jain')
        self.generate_token()

    def check_login(self):
        response = self.client.post('/rest_auth/login/', {"username": "tidu11313", "password": "14141141"})
        self.assertTrue(self.user.is_active)
        self.assertEquals(response.status_code, 200)

    def check_logout(self):
        response = self.client.get('/rest_auth/logout/',
                                   HTTP_AUTHORIZATION='TWEET {}'.format(self.user.user_token.token.decode()))
        self.assertEquals(response.status_code, 200)
