
from django.contrib.auth.models import User
from django.urls import reverse

from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token

from students.models import Student
from teachers.models import Teacher


class RegistrationTest(APITestCase):

    def test_student_register(self):
        response = self.client.post(
            reverse("student-register"),
            {
                "username": "tom",
                "password": "password123",
                "email": "tom@example.com",
                "name": "Tom",
                "student_no": "S001",
                "age": 20,
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        user = User.objects.get(username="tom")
        student = Student.objects.get(student_no="S001")

        self.assertEqual(student.user, user)
        self.assertTrue(user.check_password("password123"))
        self.assertNotEqual(user.password, "password123")

    def test_teacher_register(self):
        response = self.client.post(
            reverse("teacher-register"),
            {
                "username": "jack",
                "password": "password123",
                "email": "jack@example.com",
                "name": "Jack",
                "department": "Computer Science",
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        user = User.objects.get(username="jack")
        teacher = Teacher.objects.get(name="Jack")

        self.assertEqual(teacher.user, user)
        self.assertTrue(user.check_password("password123"))

    def test_duplicate_username(self):
        User.objects.create_user(
            username="tom",
            password="password123"
        )

        response = self.client.post(
            reverse("student-register"),
            {
                "username": "tom",
                "password": "password123",
                "name": "Tom",
                "student_no": "S001",
                "age": 20,
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_duplicate_student_no(self):
        user = User.objects.create_user(
            username="old",
            password="password123"
        )

        Student.objects.create(
            user=user,
            name="Old",
            student_no="S001",
            age=20
        )

        response = self.client.post(
            reverse("student-register"),
            {
                "username": "new",
                "password": "password123",
                "name": "New",
                "student_no": "S001",
                "age": 21,
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertFalse(
            User.objects.filter(username="new").exists()
        )

    def test_short_password(self):
        response = self.client.post(
            reverse("student-register"),
            {
                "username": "tom",
                "password": "123",
                "name": "Tom",
                "student_no": "S001",
                "age": 20,
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertFalse(
            User.objects.filter(username="tom").exists()
        )

    def test_cannot_register_as_admin(self):
        response = self.client.post(
            reverse("student-register"),
            {
                "username": "tom",
                "password": "password123",
                "name": "Tom",
                "student_no": "S001",
                "age": 20,
                "is_staff": True,
                "is_superuser": True,
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        user = User.objects.get(username="tom")

        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_register_does_not_return_password(self):
        response = self.client.post(
            reverse("student-register"),
            {
                "username": "tom",
                "password": "password123",
                "name": "Tom",
                "student_no": "S001",
                "age": 20,
            },
            format="json"
        )

        self.assertNotIn("password", response.data)
        self.assertNotIn("password", response.data["user"])


class AuthenticationTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="tom",
            password="password123",
            email="tom@example.com"
        )

        self.login_url = reverse("login")

    def test_login_success(self):
        response = self.client.post(
            self.login_url,
            {
                "username": "tom",
                "password": "password123"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertIn("token", response.data)

        token = Token.objects.get(user=self.user)

        self.assertEqual(
            response.data["token"],
            token.key
        )

    def test_wrong_password(self):
        response = self.client.post(
            self.login_url,
            {
                "username": "tom",
                "password": "wrongpassword"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_nonexistent_user(self):
        response = self.client.post(
            self.login_url,
            {
                "username": "unknown",
                "password": "password123"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_repeated_login_uses_same_token(self):
        response1 = self.client.post(
            self.login_url,
            {
                "username": "tom",
                "password": "password123"
            },
            format="json"
        )

        response2 = self.client.post(
            self.login_url,
            {
                "username": "tom",
                "password": "password123"
            },
            format="json"
        )

        self.assertEqual(
            response1.data["token"],
            response2.data["token"]
        )

        self.assertEqual(
            Token.objects.filter(user=self.user).count(),
            1
        )

    def test_login_does_not_return_password(self):
        response = self.client.post(
            self.login_url,
            {
                "username": "tom",
                "password": "password123"
            },
            format="json"
        )

        self.assertNotIn("password", response.data)
        self.assertNotIn("password", response.data["user"])

    def test_me_requires_authentication(self):
        response = self.client.get(
            reverse("current-user")
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    def test_me_returns_current_user(self):
        token = Token.objects.create(user=self.user)

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {token.key}"
        )

        response = self.client.get(
            reverse("current-user")
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data["username"],
            "tom"
        )

    def test_invalid_token(self):
        self.client.credentials(
            HTTP_AUTHORIZATION="Token invalidtoken"
        )

        response = self.client.get(
            reverse("current-user")
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    def test_logout(self):
        token = Token.objects.create(user=self.user)

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {token.key}"
        )

        response = self.client.post(
            reverse("logout")
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertFalse(
            Token.objects.filter(user=self.user).exists()
        )

    def test_old_token_invalid_after_logout(self):
        token = Token.objects.create(user=self.user)

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {token.key}"
        )

        self.client.post(reverse("logout"))

        response = self.client.get(
            reverse("current-user")
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

        self.assertTrue(
            User.objects.filter(pk=self.user.pk).exists()
        )

    def test_me_returns_student_profile(self):
        Student.objects.create(
            user=self.user,
            name="Tom",
            student_no="S001",
            age=20
        )

        token = Token.objects.create(user=self.user)

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {token.key}"
        )

        response = self.client.get(
            reverse("current-user")
        )

        self.assertEqual(
            response.data["profile"]["type"],
            "student"
        )

        self.assertEqual(
            response.data["profile"]["student_no"],
            "S001"
        )

    def test_me_returns_teacher_profile(self):
        Teacher.objects.create(
            user=self.user,
            name="Tom",
            department="Computer Science"
        )

        token = Token.objects.create(user=self.user)

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {token.key}"
        )

        response = self.client.get(
            reverse("current-user")
        )

        self.assertEqual(
            response.data["profile"]["type"],
            "teacher"
        )

    def test_admin_profile(self):
        admin = User.objects.create_superuser(
            username="admin",
            password="password123"
        )

        token = Token.objects.create(user=admin)

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {token.key}"
        )

        response = self.client.get(
            reverse("current-user")
        )

        self.assertEqual(
            response.data["profile"]["type"],
            "admin"
        )
