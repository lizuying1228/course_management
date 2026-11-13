from rest_framework.test import APITestCase
from students.models import Student
from courses.models import Course
from teachers.models import Teacher
from rest_framework import status
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.cache import cache
from rest_framework.authtoken.models import Token
from enrollments.models import Enrollment

class EnrollmentAPItest(APITestCase):
    def setUp(self):
        cache.clear()
        self.admin = User.objects.create_superuser(
            username = "admin",
            password = "password123"
        )

        self.student_a_user = User.objects.create_user(
            username = "student_a",
            password = "password123"
        )

        self.student_b_user = User.objects.create_user(
            username = "student_b",
            password = "password123"
        )

        self.teacher_a_user = User.objects.create_user(
            username = "teacher_a",
            password = "password123"
        )

        self.teacher_b_user = User.objects.create_user(
            username = "teacher_b",
            password = "password123"
        )

        self.student_a = Student.objects.create(
            user = self.student_a_user,
            name = "student_a",
            student_no = "S001",
            age = 21
        )

        self.student_b = Student.objects.create(
            user = self.student_b_user,
            name = "student_b",
            student_no = "S002",
            age = 20
        )

        self.teacher_a = Teacher.objects.create(
            user = self.teacher_a_user,
            name = "teacher_a",
            department = "讲师"
        )

        self.teacher_b = Teacher.objects.create(
            user = self.teacher_b_user,
            name = "teacher_b",
            department = "教授"
        )

        self.nomal_user = User.objects.create_user(
            username = "nomal",
            password = "password123"
        )

        self.course_a = Course.objects.create(
            teacher = self.teacher_a,
            title = "Python",
            description = "Python基础",
            capacity = 30,
            is_active = True
        )

        self.course_b = Course.objects.create(
            teacher = self.teacher_b,
            title = "Django",
            description = "Django基础",
            capacity = 1,
            is_active = True
        )

        self.course_c = Course.objects.create(
            teacher = self.teacher_a,
            title = "数据结构",
            description = "基础",
            capacity = 40,
            is_active = False
        )

        self.student_a_token = Token.objects.create(user = self.student_a_user)
        self.student_b_token = Token.objects.create(user = self.student_b_user)
        self.teacher_a_token = Token.objects.create(user = self.teacher_a_user)
        self.teacher_b_token = Token.objects.create(user = self.teacher_b_user)
        self.admin_token = Token.objects.create(user = self.admin)

    def login(self, token):
        return self.client.credentials(HTTP_AUTHORIZATION = f"Token {token}")

    def test_student_select_course(self):
        self.login(self.student_a_token)
        url = reverse("enrollment-list")
        data = {
            "course_id": self.course_a.id
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Enrollment.objects.filter(student = self.student_a, course = self.course_a).exists())

    def test_student_repeat_choose_course(self):
        self.login(self.student_a_token)
        url = reverse("enrollment-list")
        data = {
            "course_id": self.course_a.id
        }
        self.client.post(url, data, format="json")
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_choose_inactive_course(self):
        self.login(self.student_a_token)
        url = reverse("enrollment-list")
        data = {
            "course_id": self.course_c.id
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_course_capacity_full(self):
        self.login(self.student_a_token)
        Enrollment.objects.create(student = self.student_b, course = self.course_b)
        url = reverse("enrollment-list")
        data = {
            "course_id": self.course_b.id
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_student_cannot_submit_other_student_id(self):
        self.login(self.student_a_token)
        url = reverse("enrollment-list")
        data = {
            "course_id": self.course_a.id,
            "student_id": self.student_b.id
        }
        response = self.client.post(url, data, format="json")
        print("🔥 异常返回的 response.data 是：", response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("student_id", response.data.get("detail", {}))

    def test_student_can_only_view_own_enrollments(self):
        Enrollment.objects.create(student=self.student_a, course=self.course_a)
        Enrollment.objects.create(student=self.student_b, course=self.course_b)

        self.login(self.student_a_token)
        url = reverse("enrollment-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_student_cannot_delete_others_enrollment(self):
        enrollment = Enrollment.objects.create(student=self.student_b, course=self.course_a)
        
        self.login(self.student_a_token)
        url = reverse("enrollment-detail", kwargs={"pk": enrollment.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Enrollment.objects.filter(pk=enrollment.id).exists())

    def test_student_can_destroy_enrollment_and_reselect(self):
        # 课程 b 容量为 1，学生 a 先选满
        enrollment = Enrollment.objects.create(student=self.student_a, course=self.course_b)
        
        self.login(self.student_a_token)
        url = reverse("enrollment-detail", kwargs={"pk": enrollment.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Enrollment.objects.filter(pk=enrollment.id).exists())

        # 退课后释放容量，学生 b 可以重新选课
        self.login(self.student_b_token)
        list_url = reverse("enrollment-list")
        data = {"course_id": self.course_b.id}
        response = self.client.post(list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_teacher_can_only_view_own_course_enrollments(self):
        Enrollment.objects.create(student=self.student_a, course=self.course_a)
        Enrollment.objects.create(student=self.student_b, course=self.course_b)

        self.login(self.teacher_a_token)
        url = reverse("enrollment-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_admin_can_view_all_enrollments(self):
        Enrollment.objects.create(student=self.student_a, course=self.course_a)
        Enrollment.objects.create(student=self.student_b, course=self.course_b)

        self.login(self.admin_token)
        url = reverse("enrollment-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_normal_user_cannot_access_enrollment_api(self):
        normal_user_token = Token.objects.create(user=self.nomal_user)
        self.login(normal_user_token)
        url = reverse("enrollment-list")
        response = self.client.get(url)
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED])

    def test_missing_or_invalid_course_id_returns_400(self):
        self.login(self.student_a_token)
        url = reverse("enrollment-list")
        
        # 1. 缺少 course_id
        response = self.client.post(url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # 2. 参数格式错误（传字符串而非数字）
        response = self.client.post(url, {"course_id": "abc"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    

