from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User


class NoteAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )

    def test_user_registration(self):
        url = "/register/"
        data = {
            "username": "newuser",
            "password": "password123",
            "email": "user_test@gmail.com",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_note(self):
        self.client.login(username="testuser", password="testpassword")
        url = "/api/v1/notes/"
        data = {"title": "Тстовая замитка", "description": "Текставое опесание"}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(response.data["title"], "Текстовая заметка")
        self.assertEqual(response.data["description"], "Текстовое описание")

    def test_get_notes(self):
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get("/api/v1/notes/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
