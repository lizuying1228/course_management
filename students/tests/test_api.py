from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from students.models import Student

class StudentAPItest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
                username="student1", 
                password="password123"
            )
        
        self.student = Student.objects.create(
            user = self.user,
            name = "Tom",
            student_no = "S001",
            age = 20
        )

    def test_student_list(self):
        url = reverse("student-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK) 
        self.assertEqual(len(response.data), 1)

    def test_student_detail(self):
        url = reverse("student-detail", args = [self.student.pk])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Tom")

    def test_student_not_found(self):
        url = reverse("student-detail", args = [999])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_student_create(self):
        user = User.objects.create_user(
            username = "student2",
            password = "password123"
        )

        data = {
            "user_id": user.id,
            "name": "Alice",
            "student_no": "S002",
            "age": 19
        }

        url = reverse("student-list")
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        exist = Student.objects.filter(student_no = "S002").exists()
        self.assertTrue(exist)

    def test_student_update(self):
        url = reverse("student-detail", args = [self.student.pk])

        data = {
            "name": "Tom update",
            "student_no": "S001",
            "age": 21
        }

        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.student.refresh_from_db()
        self.assertEqual(self.student.age, 21)

    def test_student_patch(self):
        url = reverse("student-detail", args = [self.student.pk])

        data = {
            "age": 22
        }

        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.student.refresh_from_db()
        self.assertEqual(self.student.age, 22)
        self.assertEqual(self.student.name, "Tom")

    def test_student_method_not_allowed(self):
        url = reverse("student-list")

        response = self.client.put(url, {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_student_create_noname(self):
        user = User.objects.create_user(
            username = "student3",
            password = "password123"
        )

        url = reverse("student-list")

        data = {
            "user_id": user.id,
            "student_no": "S004",
            "age": 21
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_student_delete(self):
        url = reverse("student-detail", args = [self.student.pk])

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        exist = Student.objects.filter(pk = self.student.pk).exists()
        self.assertFalse(exist)

    def test_student_no_user_id(self):
        data = {
            "name": "Ammy",
            "student_no": "S006",
            "age": 18
        }

        url = reverse("student-list")
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
