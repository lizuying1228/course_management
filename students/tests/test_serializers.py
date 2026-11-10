from django.test import TestCase
from django.contrib.auth.models import User
from students.models import Student
from students.serializers import StudentSerializer
# Create your tests here.
class StudentSerializerTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username = "alice",
            password = "123456alice"
        )

        self.student = Student.objects.create(
            user = self.user,
            name = "Alice",
            student_no = "2026001",
            age = 21
        )

    def test_valid_data(self):
        data = {
            "name": "Bob",
            "student_no": "2026002",
            "age": 22
        }

        serializer = StudentSerializer(data = data)

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_student_age(self):
        data = {
            "name": "Bob",
            "student_no": "2026002",
            "age": 0
        }

        serializer = StudentSerializer(data = data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("age", serializer.errors)

    def test_missing_name(self):
        data = {
            "student_no": "2026002",
            "age": 21
        }

        serializer = StudentSerializer(data = data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)

    def test_missing_student_no(self):
        data = {
            "name": "Bob",
            "age": 21
        }

        serializer = StudentSerializer(data = data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("student_no", serializer.errors)

    def test_duplicate_student_no(self):
        data = {
            "name": "Bob",
            "student_no": "2026001",
            "age": 21
        }

        serializer = StudentSerializer(data = data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("student_no", serializer.errors)

    def test_update_student_no(self):
        data = {
            "name": "Alice update",
            "student_no": "2026001",
            "age": 21
        }

        serializer = StudentSerializer(instance=self.student, data = data)

        self.assertTrue(serializer.is_valid(), serializer.errors)