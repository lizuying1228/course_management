
from django.contrib.auth.models import User

from rest_framework.test import APITestCase
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.test import APIRequestFactory

from users.permissions import (
    IsAdminUser,
    IsTeacher,
    IsStudent,
    IsStudentOrAdmin,
    IsTeacherOrAdmin,
)

from students.models import Student
from teachers.models import Teacher


class PermissionTestView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "ok"})


class RolePermissionTest(APITestCase):

    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="admin",
            password="password123"
        )

        self.teacher_user = User.objects.create_user(
            username="teacher",
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

        Teacher.objects.create(
            user=self.teacher_user,
            name="Teacher",
            department="Computer Science"
        )

        Student.objects.create(
            user=self.student_user,
            name="Student",
            student_no="S001",
            age=20
        )

    def check_permission(self, user, permission_class):
        factory = APIRequestFactory()
        request = factory.get("/")
        request.user = user

        view = PermissionTestView()
        view.action = "list"

        permission = permission_class()

        return permission.has_permission(request, view)

    def test_is_admin(self):
        self.assertTrue(
            self.check_permission(
                self.admin,
                IsAdminUser
            )
        )

        self.assertFalse(
            self.check_permission(
                self.teacher_user,
                IsAdminUser
            )
        )

    def test_is_teacher(self):
        self.assertTrue(
            self.check_permission(
                self.teacher_user,
                IsTeacher
            )
        )

        self.assertFalse(
            self.check_permission(
                self.student_user,
                IsTeacher
            )
        )

    def test_is_student(self):
        self.assertTrue(
            self.check_permission(
                self.student_user,
                IsStudent
            )
        )

        self.assertFalse(
            self.check_permission(
                self.teacher_user,
                IsStudent
            )
        )

    def test_is_student_or_admin(self):
        self.assertTrue(
            self.check_permission(
                self.student_user,
                IsStudentOrAdmin
            )
        )

        self.assertTrue(
            self.check_permission(
                self.admin,
                IsStudentOrAdmin
            )
        )

        self.assertFalse(
            self.check_permission(
                self.teacher_user,
                IsStudentOrAdmin
            )
        )

    def test_is_teacher_or_admin(self):
        self.assertTrue(
            self.check_permission(
                self.teacher_user,
                IsTeacherOrAdmin
            )
        )

        self.assertTrue(
            self.check_permission(
                self.admin,
                IsTeacherOrAdmin
            )
        )

        self.assertFalse(
            self.check_permission(
                self.student_user,
                IsTeacherOrAdmin
            )
        )
