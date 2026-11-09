from django.test import TestCase
from django.contrib.auth.models import User
from teachers.models import Teacher
from teachers.serializers import TeacherSerializer
# Create your tests here.
class TeacherSerializerTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username = "alice",
            password = "123456alice"
        )

        self.teacher = Teacher.objects.create(
            user = self.user,
            name = "Alice",
            department = "副教授"
        )

    def test_valid_data(self):
        data = {
            "name": "Bob",
            "department": "教授"
        }

        serializer = TeacherSerializer(data = data)

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_missing_department(self):
        data = {
            "name": "Bob",
            "department": ""
        }

        serializer = TeacherSerializer(data = data)

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_missing_name(self):
        data = {
            "department": "教授"
        }

        serializer = TeacherSerializer(data = data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)

    