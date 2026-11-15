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

    def test_admin_can_retrieve_student_detail(self):
        self.login(self.admin_token)
        response = self.client.get(reverse("student-detail", args=[self.student_a.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["student_no"], "S001")

    def test_admin_can_create_student_and_user_together(self):
        self.login(self.admin_token)
        response = self.client.post(reverse("student-list"), {
            "username": "new_student",
            "password": "password123",
            "name": "New Student",
            "student_no": "S003",
            "age": 19,
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="new_student").exists())
        self.assertTrue(Student.objects.filter(student_no="S003").exists())

    def test_admin_soft_delete_student_and_restore(self):
        self.login(self.admin_token)
        detail_url = reverse("student-detail", args=[self.student_a.id])
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.student_a_user.refresh_from_db()
        self.assertFalse(self.student_a_user.is_active)
        self.assertTrue(Student.objects.filter(pk=self.student_a.pk).exists())
        self.assertFalse(Token.objects.filter(user=self.student_a_user).exists())

        response = self.client.post(reverse("student-restore", args=[self.student_a.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.student_a_user.refresh_from_db()
        self.assertTrue(self.student_a_user.is_active)

    def test_soft_deleted_student_old_token_is_invalid(self):
        old_token_key = self.student_a_token.key
        self.login(self.admin_token)
        self.client.delete(reverse("student-detail", args=[self.student_a.id]))
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {old_token_key}")
        response = self.client.get(reverse("student-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_admin_can_search_student_by_id(self):
        self.login(self.admin_token)
        response = self.client.get(reverse("student-list"), {"id": self.student_b.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], self.student_b.id)
