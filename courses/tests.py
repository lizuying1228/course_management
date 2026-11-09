from django.test import TestCase
from django.contrib.auth.models import User
from teachers.models import Teacher
from courses.models import Course
from courses.serializers import CourseSerializer
# Create your tests here.
class CourseSerializerTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username = "alice",
            password = "123456alice"
        )

        self.teacher = Teacher.objects.create(
            user = self.user,
            name = "Alice",
            department = "教授"
        )

    def test_valid_data(self):
        data = {
            "title": "Python Web开发基础",
            "description": "Python Introduction",
            "capacity": 30
        }

        serializer = CourseSerializer(data = data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_missing_title(self):
        data = {
            "description": "Python Introduction",
            "capacity": 30
        }

        serializer = CourseSerializer(data = data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("title", serializer.errors)

    def test_missing_description(self):
        data = {
            "title": "Python Web开发基础",
            "capacity": 30
        }

        serializer = CourseSerializer(data = data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_course_capacity(self):
        data = {
            "title": "Python Web开发基础",
            "description": "Python Introduction",
            "capacity": 0
        }

        serializer = CourseSerializer(data = data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("capacity", serializer.errors)

    def test_course_teacher(self):
        data = {
            "teacher": self.teacher.pk,
            "title": "Python Web开发基础",
            "description": "Python Introduction",
            "capacity": 30
        }

        serializer = CourseSerializer(data = data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertNotIn("teacher", serializer.validated_data)
        
