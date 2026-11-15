from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from teachers.models import Teacher


class TeacherAdminAPITest(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="admin_teacher_test", password="password123"
        )
        token = Token.objects.create(user=self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def test_admin_can_create_teacher_and_user_together(self):
        response = self.client.post(
            reverse("teacher-list"),
            {
                "username": "created_teacher",
                "password": "password123",
                "name": "Created Teacher",
                "department": "Computer Science",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="created_teacher").exists())
        self.assertTrue(Teacher.objects.filter(name="Created Teacher").exists())
