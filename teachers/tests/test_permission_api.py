
from django.contrib.auth.models import User
from django.urls import reverse

from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from rest_framework import status

from students.models import Student
from teachers.models import Teacher


class TeacherPermissionAPITest(APITestCase):

    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="admin",
            password="password123"
        )

        self.teacher_a_user = User.objects.create_user(
            username="teacher_a",
            password="password123"
        )

        self.teacher_b_user = User.objects.create_user(
            username="teacher_b",
            password="password123"
        )

        self.student_user = User.objects.create_user(
            username="student",
            password="password123"
        )

        self.normal_user = User.objects.create_user(
            username="normal",
            password="password123"
        )

        self.teacher_a = Teacher.objects.create(
            user=self.teacher_a_user,
            name="Teacher A",
            department="CS"
        )

        self.teacher_b = Teacher.objects.create(
            user=self.teacher_b_user,
            name="Teacher B",
            department="Math"
        )

        Student.objects.create(
            user=self.student_user,
            name="Student",
            student_no="S001",
            age=20
        )

        self.admin_token = Token.objects.create(user=self.admin)
        self.teacher_a_token = Token.objects.create(user=self.teacher_a_user)
        self.teacher_b_token = Token.objects.create(user=self.teacher_b_user)
        self.student_token = Token.objects.create(user=self.student_user)
        self.normal_token = Token.objects.create(user=self.normal_user)

    def login(self, token):
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {token.key}"
        )

    def test_admin_can_view_all_teachers(self):
        self.login(self.admin_token)

        response = self.client.get(
            reverse("teacher-list")
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_teacher_can_view_all_teachers(self):
        self.login(self.teacher_a_token)

        response = self.client.get(
            reverse("teacher-list")
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_teacher_can_update_self(self):
        self.login(self.teacher_a_token)

        response = self.client.patch(
            reverse(
                "teacher-detail",
                args=[self.teacher_a.id]
            ),
            {"department": "AI"},
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.teacher_a.refresh_from_db()
        self.assertEqual(self.teacher_a.department, "AI")

    def test_teacher_cannot_update_other_teacher(self):
        self.login(self.teacher_a_token)

        response = self.client.patch(
            reverse(
                "teacher-detail",
                args=[self.teacher_b.id]
            ),
            {"department": "AI"},
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_teacher_cannot_delete_self(self):
        self.login(self.teacher_a_token)

        response = self.client.delete(
            reverse(
                "teacher-detail",
                args=[self.teacher_a.id]
            )
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_can_view_teachers(self):
        self.login(self.student_token)

        response = self.client.get(
            reverse("teacher-list")
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_student_cannot_update_teacher(self):
        self.login(self.student_token)

        response = self.client.patch(
            reverse(
                "teacher-detail",
                args=[self.teacher_a.id]
            ),
            {"department": "AI"},
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_normal_user_cannot_access(self):
        self.login(self.normal_token)

        response = self.client.get(
            reverse("teacher-list")
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_anonymous_user_cannot_access(self):
        response = self.client.get(
            reverse("teacher-list")
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    def test_admin_can_create_teacher(self):
        self.login(self.admin_token)

        new_user = User.objects.create_user(
            username="new_teacher",
            password="password123"
        )

        response = self.client.post(
            reverse("teacher-list"),
            {
                "user_id": new_user.id,
                "name": "New Teacher",
                "department": "AI"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        teacher = Teacher.objects.get(name="New Teacher")
        self.assertEqual(teacher.user, new_user)
