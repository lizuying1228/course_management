from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from students.models import Student
from teachers.models import Teacher
from rest_framework.authtoken.models import Token
from django.urls import reverse
from rest_framework import status


class StudentPermissionTest(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username = "admin",
            password = "password123"
        )

        self.student_a_user = User.objects.create_user(
            username = "student_a",
            password = "password123"
        )

        self.student_b_user = User.objects.create_user(
            username = "student_b",
            password = "password123"
        )

        self.teacher_user = User.objects.create_user(
            username = "teacher",
            password = "password123"
        )

        self.student_a = Student.objects.create(
            user = self.student_a_user,
            name = "student_a",
            student_no = "S001",
            age = 21
        )

        self.student_b = Student.objects.create(
            user = self.student_b_user,
            name = "student_b",
            student_no = "S002",
            age = 20
        )

        self.teacher = Teacher.objects.create(
            user = self.teacher_user,
            name = "teacher",
            department = "讲师"
        )

        self.nomal_user = User.objects.create_user(
            username = "nomal",
            password = "password123"
        )

        self.student_a_token = Token.objects.create(user = self.student_a_user)
        self.student_b_token = Token.objects.create(user = self.student_b_user)
        self.teacher_token = Token.objects.create(user = self.teacher_user)
        self.admin_token = Token.objects.create(user = self.admin)

    def login(self, token):
        self.client.credentials(HTTP_AUTHORIZATION = f"Token {token.key}")

    def test_admin_list(self):
        self.login(self.admin_token)
        url = reverse("student-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_teacher_list(self):
        self.login(self.teacher_token)
        url = reverse("student-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_student_view_self(self):
        self.login(self.student_a_token)
        url = reverse("student-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["student_no"], "S001")

    def test_student_cannot_view_other(self):
        self.login(self.student_a_token)
        url = reverse("student-detail", args = [self.student_b.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_student_update_self(self):
        self.login(self.student_a_token)
        url = reverse("student-detail", args = [self.student_a.id])
        data = {
            "name": "student_a",
            "student_no": "S001",
            "age": 24
        }
        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.student_a.refresh_from_db()
        self.assertEqual(self.student_a.age, 24)
        self.assertEqual(self.student_a.name, "student_a")

    def test_student_cannot_update_other(self):
        self.login(self.student_a_token)
        url = reverse("student-detail", args = [self.student_b.id])
        data = {
            "name": "student_b",
            "student_no": "S002",
            "age": 24
        }
        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_student_cannot_delete(self):
        self.login(self.student_a_token)
        url = reverse("student-detail", args = [self.student_a.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_teacher_cannot_update(self):
        self.login(self.teacher_token)
        url = reverse("student-detail", args = [self.student_a.id])
        data = {
            "name": "student_a",
            "student_no": "S001",
            "age": 24
        }
        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_nomal_cannot_view(self):
        url = reverse("student-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)





