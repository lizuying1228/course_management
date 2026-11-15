from django.test import TestCase
from django.contrib.auth.models import User
from students.models import Student
from teachers.models import Teacher
from courses.models import Course
from enrollments.models import Enrollment
from enrollments.serializers import EnrollmentSerializer, EnrollmentCreateSerializer
# Create your tests here.
class EnrollmentSerializerTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username = "alice",
            password = "123456alice"
        )

        self.student = Student.objects.create(
            user = self.user,
            name = "Alice",
            student_no = "2026001",
            age = 19
        )

        teacher_user = User.objects.create_user(
            username = "bob",
            password = "123456bob"
        )

        self.teacher = Teacher.objects.create(
            user = teacher_user,
            name = "Bob",
            department = "讲师"
        )

        self.course = Course.objects.create(
            teacher=self.teacher,
            title="Python",
            capacity=30,
            is_active=True,
        )

    def test_valid_data(self):
        data = {
            "course": self.course.pk
        }
        context = {
            "student": self.student
        }

        serializer = EnrollmentSerializer(data = data, context = context)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_duplicate_course(self):
        Enrollment.objects.create(student = self.student, course = self.course)
        data = {
            "course_id": self.course.pk
        }
        context = {
            "student": self.student
        }

        serializer = EnrollmentCreateSerializer(data = data, context = context)
        self.assertFalse(serializer.is_valid())
        self.assertIn("course", serializer.errors)

    def test_inactive_course(self):
        self.course.is_active = False
        self.course.save()

        data = {
            "course_id": self.course.pk
        }
        context = {
            "student": self.student
        }

        serializer = EnrollmentCreateSerializer(data = data, context = context)
        self.assertFalse(serializer.is_valid())
        self.assertIn("course_id", serializer.errors)

    def test_noneexist_course(self):
        data = {
            "course_id": 99999
        }
        context = {
            "student": self.student
        }

        serializer = EnrollmentCreateSerializer(data = data, context = context)
        self.assertFalse(serializer.is_valid())
        self.assertIn("course_id", serializer.errors)

    def test_student_only_read(self):
        another_user = User.objects.create_user(
            username = "tom",
            password = "123456tom"
        )

        another_student = Student.objects.create(
            user = another_user,
            name = "Tom",
            student_no = "2026002",
            age = 20
        )

        data = {
            "student": another_student.pk,
            "course": self.course.pk
        }
        context = {
            "student": self.student
        }

        serializer = EnrollmentSerializer(data = data, context = context)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertNotIn("student", serializer.validated_data)