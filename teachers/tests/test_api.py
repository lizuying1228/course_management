from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from teachers.serializers import TeacherSerializer
from teachers.models import Teacher
from django.urls import reverse
from rest_framework import status

class TeacherAPItest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username = "teacher1",
            password = "password123"
        )

        self.teacher = Teacher.objects.create(
            user = self.user,
            name = "Alice",
            department = "讲师"
        )

    def test_teacher_list(self):
        url = reverse("teacher-list")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_teacher_detail(self):
        url = reverse("teacher-detail", args = [self.teacher.pk])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Alice")

    def test_teacher_create(self):
        user = User.objects.create_user(
            username = "teacher2",
            password = "password123"
        )

        data = {
            "user_id": user.id,
            "name": "Tom"
        }

        url = reverse("teacher-list")
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        exist = Teacher.objects.filter(name = "Tom").exists()
        self.assertTrue(exist)

    def test_teacher_update(self):
        data = {
            "name": "Alice update",
            "department": "教授"
        }

        url = reverse("teacher-detail", args = [self.teacher.pk])
        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.teacher.refresh_from_db()
        self.assertEqual(self.teacher.department, "教授")

    def test_teacher_partial_update(self):
        data = {"name": "alice"}

        url = reverse("teacher-detail", args = [self.teacher.pk])
        response = self.client.patch(url, data, format = "json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.teacher.refresh_from_db()
        self.assertEqual(self.teacher.name, "alice")
        self.assertEqual(self.teacher.department, "讲师")

    def test_teacher_not_found(self):
        url = reverse("teacher-detail", args = [999])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        

