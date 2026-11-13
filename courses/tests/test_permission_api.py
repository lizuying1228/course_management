
from django.contrib.auth.models import User
from django.urls import reverse

from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from rest_framework import status

from students.models import Student
from teachers.models import Teacher
from courses.models import Course


class CoursePermissionAPITest(APITestCase):

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

        self.course_a = Course.objects.create(
            teacher=self.teacher_a,
            title="Python",
            description="Python course",
            capacity=30,
            is_active=True
        )

        self.course_b = Course.objects.create(
            teacher=self.teacher_b,
            title="CUDA",
            description="CUDA course",
            capacity=20,
            is_active=True
        )

        self.inactive_course = Course.objects.create(
            teacher=self.teacher_b,
            title="Old Course",
            capacity=20,
            is_active=False
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

    def test_admin_can_view_all_courses(self):
        self.login(self.admin_token)

        response = self.client.get(
            reverse("course-list")
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 3)

    def test_teacher_can_view_all_courses(self):
        self.login(self.teacher_a_token)

        response = self.client.get(
            reverse("course-list")
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 3)

    def test_teacher_can_update_own_course(self):
        self.login(self.teacher_a_token)

        response = self.client.patch(
            reverse(
                "course-detail",
                args=[self.course_a.id]
            ),
            {"title": "Advanced Python"},
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.course_a.refresh_from_db()
        self.assertEqual(self.course_a.title, "Advanced Python")

    def test_teacher_cannot_update_other_course(self):
        self.login(self.teacher_a_token)

        response = self.client.patch(
            reverse(
                "course-detail",
                args=[self.course_b.id]
            ),
            {"title": "Changed"},
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_teacher_can_create_course_for_self(self):
        self.login(self.teacher_a_token)

        response = self.client.post(
            reverse("course-list"),
            {
                "title": "New Python",
                "description": "New course",
                "capacity": 40,
                "teacher_id": self.teacher_b.id
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        course = Course.objects.get(title="New Python")

        # 即使客户端提交了 teacher_id，也必须关联当前教师
        self.assertEqual(course.teacher, self.teacher_a)

    def test_teacher_cannot_delete_other_course(self):
        self.login(self.teacher_a_token)

        response = self.client.delete(
            reverse(
                "course-detail",
                args=[self.course_b.id]
            )
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_can_only_view_active_courses(self):
        self.login(self.student_token)

        response = self.client.get(
            reverse("course-list")
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

        titles = [item["title"] for item in response.data["results"]]

        self.assertIn("Python", titles)
        self.assertIn("CUDA", titles)
        self.assertNotIn("Old Course", titles)

    def test_student_cannot_view_inactive_course_detail(self):
        self.login(self.student_token)

        response = self.client.get(
            reverse(
                "course-detail",
                args=[self.inactive_course.id]
            )
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_student_can_view_active_courses_action(self):
        self.login(self.student_token)

        response = self.client.get(
            reverse("course-active")
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_student_cannot_create_course(self):
        self.login(self.student_token)

        response = self.client.post(
            reverse("course-list"),
            {
                "title": "New Course",
                "capacity": 30
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_cannot_update_course(self):
        self.login(self.student_token)

        response = self.client.patch(
            reverse(
                "course-detail",
                args=[self.course_a.id]
            ),
            {"title": "Changed"},
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_cannot_delete_course(self):
        self.login(self.student_token)

        response = self.client.delete(
            reverse(
                "course-detail",
                args=[self.course_a.id]
            )
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_create_course_for_selected_teacher(self):
        self.login(self.admin_token)

        response = self.client.post(
            reverse("course-list"),
            {
                "title": "Admin Created Course",
                "capacity": 50,
                "teacher_id": self.teacher_b.id
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        course = Course.objects.get(title="Admin Created Course")

        self.assertEqual(course.teacher, self.teacher_b)

    def test_normal_user_cannot_access(self):
        self.login(self.normal_token)

        response = self.client.get(
            reverse("course-list")
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_anonymous_user_cannot_access(self):
        response = self.client.get(
            reverse("course-list")
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )
