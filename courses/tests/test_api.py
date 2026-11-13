from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from courses.models import Course
from teachers.models import Teacher
from rest_framework.authtoken.models import Token

# class CourseAPItest(APITestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(
#             username = "alice",
#             password = "password123"
#         )
        
#         token = Token.objects.create(user = self.user)
#         self.client.credentials(HTTP_AUTHORIZATION = f"Token {token}")

#         self.teacher = Teacher.objects.create(
#             user = self.user,
#             name = "Alice"
#         )

#         self.course = Course.objects.create(
#             teacher = self.teacher, 
#             title = "Python",
#             description = "111",
#             capacity = 30,
#             is_active = True 
#         )

#     def test_course_list(self):
#         url = reverse("course-list")
#         response = self.client.get(url)

#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data), 1)

#     def test_course_create(self):
#         data = {
#             "teacher_id": self.teacher.id,
#             "title": "Java",
#             "description": "222",
#             "capacity": 20,
#             "is_active": False
#         }

#         url = reverse("course-list")
#         response = self.client.post(url, data, format="json")

#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)

#         self.assertTrue(
#             Course.objects.filter(title="Java").exists()
#         )

#     def test_course_partial_update(self):
#         data = {
#             "title": "Python 开发"
#         }

#         url = reverse("course-detail", args = [self.course.pk])
#         response = self.client.patch(url, data, format="json")

#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.course.refresh_from_db()
#         self.assertEqual(self.course.capacity, 30)
#         self.assertEqual(self.course.title, "Python 开发")

#     def test_course_not_found(self):
#         url = reverse("course-detail", args = [999])
#         response = self.client.get(url)

#         self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

#     def test_course_invalid_teacher(self):
#         url = reverse("course-list")

#         data = {
#             "teacher_id": 9999,
#             "title": "Java",
#             "description": "222",
#             "capacity": 20,
#             "is_active": False            
#         }

#         response = self.client.post(url, data, format="json")

#         self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

#     def test_course_invalid_capacity(self):
#         url = reverse("course-list")

#         data = {
#             "teacher_id": self.teacher.id,
#             "title": "Java",
#             "description": "222",
#             "capacity": 0,
#             "is_active": False            
#         }

#         response = self.client.post(url, data, format="json")

#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

#     def test_course_delete(self):
#         url = reverse("course-detail", args = [self.course.pk])

#         response = self.client.delete(url)

#         self.assertEqual(
#             response.status_code,
#             status.HTTP_204_NO_CONTENT
#         )
#         self.assertFalse(
#             Course.objects.filter(pk=self.course.pk).exists()
#         )

