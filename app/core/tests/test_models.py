from django.test import TestCase
from django.contrib.auth import get_user_model
# noinspection PyUnresolvedReferences
from core import models


def sample_user(email='test@mkznd.com', password='password', name='Tester'):
    """Creates a sample user with default or provided parameters"""
    return get_user_model().objects.create_user(
        email=email,
        password=password,
        name=name
    )


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

        email = 'Test@MKZND.com'
        normalized_email = 'Test@mkznd.com'
        password = '12345'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, normalized_email)

    def test_new_user_invalid_email_error(self):
        """Tests if the user creation is failed
        whenever incorrect email is provided"""

        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, '1234')

    def test_create_new_superuser(self):
        """Tests creating a new superuser
        and adding its is_staff and is_superuser"""

        email = 'test@mkznd.com'
        user = get_user_model().objects.create_superuser(
            email=email,
            password='12345'
        )
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_tag_str(self):
        """Test tag string representation"""
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Vegan'
        )

        self.assertEqual(str(tag), tag.name)
