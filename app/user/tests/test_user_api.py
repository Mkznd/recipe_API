from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserAPITests(TestCase):
    """Tests the users API unauthenticated(create user only)"""

    def setUp(self):
        self.client = APIClient()
        self.payload = {
            'email': 'test@mkznd.com',
            'password': 'abc12345',
            'name': 'Tester'
        }

    def test_create_valid_user(self):
        """Test that creating a user with valid payload is successful"""
        res = self.client.post(CREATE_USER_URL, self.payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(self.payload['password']))
        self.assertNotIn('password', res.data)

    def user_exists(self):
        """Test creating a user that already exists fails"""
        create_user(**self.payload)

        res = self.client.post(CREATE_USER_URL, self.payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that user with a short password is not created"""
        self.payload['password'] = 'pw'
        res = self.client.post(CREATE_USER_URL, self.payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.all().filter(
            email=self.payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_normal_password(self):
        """Test that user with normal password is created successfully"""
        res = self.client.post(CREATE_USER_URL, self.payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user_exists = get_user_model().objects.all().filter(
            email=self.payload['email']
        ).exists()
        self.assertTrue(user_exists)

    def test_create_token_for_user(self):
        """Test that the token is created for user"""
        create_user(**self.payload)
        res = self.client.post(TOKEN_URL, self.payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """Test that token is not created if invalid credentials are given"""
        create_user(**self.payload)
        self.payload['password'] = 'wrong'
        res = self.client.post(TOKEN_URL, self.payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_create_token_without_user(self):
        """Test that token is not created if the user does not exist"""
        res = self.client.post(TOKEN_URL, self.payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_create_token_missing_email(self):
        """Test that email is required for token creation"""
        self.payload['email'] = ''
        res = self.client.post(TOKEN_URL, self.payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_create_token_missing_password(self):
        """Test that password is required for token creation"""
        self.payload['password'] = ''
        res = self.client.post(TOKEN_URL, self.payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)
