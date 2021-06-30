from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """Tests creating user model with a correct email"""
        email = 'test@mkznd.com'
        password = '12345'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Tests if new user email is normalized
        (email domain in all lowercase)"""

        email = "test@MKZND.com"
        password = '12345'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email_error(self):
        """Tests if the user creation is failed
        whenever incorrect email is provided"""

        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, '1234')
