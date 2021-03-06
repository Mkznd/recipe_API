from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient
from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipe:ingredient-list')


class PublicIngredientAPITests(TestCase):
    """Test the publicly available ingredient API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required to access API"""
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientAPITests(TestCase):
    """Test the private ingredient API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='test@mkznd.com',
            password='password'
        )
        self.client.force_authenticate(user=self.user)

    def test_get_ingredient_list(self):
        """Test retrieving a list of ingredients"""
        Ingredient.objects.create(user=self.user, name='Kale')
        Ingredient.objects.create(user=self.user, name='Salt')
        res = self.client.get(INGREDIENTS_URL)

        ingredients_db = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients_db, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test that only ingredients for authenticated user are returned"""
        user2 = get_user_model().objects.create_user(
            email='new@mkznd.com',
            password='password'
        )
        ingredient = Ingredient.objects.create(user=self.user, name='Kale')
        Ingredient.objects.create(user=user2, name='Apple')

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)

    def test_create_ingredient(self):
        """Test that ingredient with normal name can be created"""
        payload = {'name': 'Celery'}
        res = self.client.post(INGREDIENTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        exists = Ingredient.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()
        self.assertTrue(exists)

    def test_create_without_name(self):
        """Test if creating ingredient without name fails"""
        payload = {'name': ''}
        res = self.client.post(INGREDIENTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        exists = Ingredient.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()
        self.assertFalse(exists)

    def test_create_existing_name(self):
        """Test if creating existing ingredients fails"""
        payload = {'name': 'Cabbage'}
        Ingredient.objects.create(user=self.user, name='Cabbage')
        res = self.client.post(INGREDIENTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        num = len(Ingredient.objects.filter(
            user=self.user,
            name=payload['name']
        ))
        self.assertEqual(num, 1)
