
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from django.core.cache import cache

from students.models import Student
from teachers.models import Teacher
from courses.models import Course
from enrollments.models import Enrollment



class EnrollmentAPIFeaturesTest(APITestCase):

    def setUp(self):
        cache.clear()
        # 管理员
        self.admin = User.objects.create_superuser(
            username="admin",
            password="password123",
            email="admin@example.com",
        )

        # 两位教师
        self.teacher_users = []
        self.teachers = []

        for i in range(2):
            user = User.objects.create_user(
                username=f"teacher{i}",
                password="password123",
            )

            teacher = Teacher.objects.create(
                user=user,
                name=f"Teacher {i}",
                department="Computer Science",
            )

            self.teacher_users.append(user)
            self.teachers.append(teacher)

        # 创建12门课程，每位教师负责6门
        self.courses = []

        for i in range(12):
            teacher = self.teachers[i % 2]

            course = Course.objects.create(
                teacher=teacher,
                title=f"Python Course {i:02d}" if i % 2 == 0
                      else f"Django Course {i:02d}",
                description=f"Backend Course {i}",
                capacity=30,
                is_active=True,
            )

            self.courses.append(course)

        # 创建5名学生
        self.students = []
        self.student_users = []

        for i in range(5):
            user = User.objects.create_user(
                username=f"student{i}",
                password="password123",
            )

            student = Student.objects.create(
                user=user,
                name=f"Student {i}",
                student_no=f"S{i:03}",
                age=20,
            )

            self.student_users.append(user)
            self.students.append(student)

        # 每名学生选择全部12门课程
        # 总共60条选课记录
        self.enrollments = []

        for student in self.students:
            for course in self.courses:
                enrollment = Enrollment.objects.create(
                    student=student,
                    course=course,
                )

                self.enrollments.append(enrollment)

    def get_results(self, response):
        self.assertEqual(response.status_code, 200)
        self.assertIn("results", response.data)
        return response.data["results"]

    def authenticate(self, user):
        self.client = APIClient()
        self.client.force_authenticate(user=user)

    # -------------------------
    # 一、过滤测试
    # -------------------------

    def test_filter_by_course(self):
        self.authenticate(self.admin)

        course = self.courses[0]

        response = self.client.get(
            f"/api/enrollments/?course={course.id}"
        )

        self.get_results(response)

        expected_count = Enrollment.objects.filter(
            course=course
        ).count()

        self.assertEqual(response.data["count"], expected_count)

    def test_filter_by_student(self):
        self.authenticate(self.admin)

        student = self.students[0]

        response = self.client.get(
            f"/api/enrollments/?student={student.id}"
        )

        self.get_results(response)

        expected_count = Enrollment.objects.filter(
            student=student
        ).count()

        self.assertEqual(response.data["count"], expected_count)

    # -------------------------
    # 二、搜索测试
    # -------------------------

    def test_search_by_student_name(self):
        self.authenticate(self.admin)

        response = self.client.get(
            "/api/enrollments/?search=S001"
        )

        self.get_results(response)

        expected_count = Enrollment.objects.filter(
            student__student_no__icontains="S001"
        ).count()

        self.assertEqual(response.data["count"], expected_count)

    def test_search_by_student_number(self):
        self.authenticate(self.admin)

        response = self.client.get(
            "/api/enrollments/?search=S000"
        )

        self.get_results(response)

        expected_count = Enrollment.objects.filter(
            student__student_no__icontains="S000"
        ).count()

        self.assertEqual(response.data["count"], expected_count)

    def test_search_by_course_title(self):
        self.authenticate(self.admin)

        response = self.client.get(
            "/api/enrollments/?search=Python"
        )

        self.get_results(response)

        expected_count = Enrollment.objects.filter(
            course__title__icontains="Python"
        ).count()

        self.assertEqual(response.data["count"], expected_count)

    # -------------------------
    # 三、排序测试
    # -------------------------

    def test_ordering_by_student_name(self):
        self.authenticate(self.admin)

        response = self.client.get(
            "/api/enrollments/?ordering=student__name"
        )

        self.get_results(response)

        actual_ids = [
            item["id"] for item in response.data["results"]
        ]

        expected_ids = list(
            Enrollment.objects.order_by(
                "student__name"
            ).values_list("id", flat=True)[:10]
        )

        self.assertEqual(actual_ids, expected_ids)

    def test_ordering_by_course_title(self):
        self.authenticate(self.admin)

        response = self.client.get(
            "/api/enrollments/?ordering=course__title"
        )

        self.get_results(response)

        actual_ids = [
            item["id"] for item in response.data["results"]
        ]

        expected_ids = list(
            Enrollment.objects.order_by(
                "course__title"
            ).values_list("id", flat=True)[:10]
        )

        self.assertEqual(actual_ids, expected_ids)

    # -------------------------
    # 四、分页测试
    # -------------------------

    def test_default_pagination(self):
        self.authenticate(self.admin)

        response = self.client.get("/api/enrollments/")

        results = self.get_results(response)

        self.assertEqual(response.data["count"], 60)
        self.assertEqual(len(results), 10)

    def test_second_page(self):
        self.authenticate(self.admin)

        response1 = self.client.get(
            "/api/enrollments/?page=1"
        )

        response2 = self.client.get(
            "/api/enrollments/?page=2"
        )

        results1 = self.get_results(response1)
        results2 = self.get_results(response2)

        ids1 = {item["id"] for item in results1}
        ids2 = {item["id"] for item in results2}

        self.assertEqual(len(results1), 10)
        self.assertEqual(len(results2), 10)
        self.assertTrue(ids1.isdisjoint(ids2))

    def test_custom_page_size(self):
        self.authenticate(self.admin)

        response = self.client.get(
            "/api/enrollments/?page_size=20"
        )

        results = self.get_results(response)

        self.assertEqual(len(results), 20)

    def test_max_page_size(self):
        self.authenticate(self.admin)

        response = self.client.get(
            "/api/enrollments/?page_size=100"
        )

        results = self.get_results(response)

        self.assertEqual(len(results), 50)

    # -------------------------
    # 五、组合测试
    # -------------------------

    def test_filter_search_ordering_pagination_together(self):
        self.authenticate(self.admin)

        course = self.courses[0]

        response = self.client.get(
            f"/api/enrollments/"
            f"?course={course.id}"
            f"&search=Student"
            f"&ordering=student__name"
            f"&page=1"
            f"&page_size=2"
        )

        results = self.get_results(response)

        self.assertEqual(response.data["count"], 5)
        self.assertEqual(len(results), 2)

    # -------------------------
    # 六、数据隔离测试
    # -------------------------

    def test_student_can_only_see_own_enrollments(self):
        student = self.students[0]

        self.authenticate(student.user)

        response = self.client.get("/api/enrollments/")

        results = self.get_results(response)

        self.assertEqual(response.data["count"], 12)

        expected_ids = set(
            Enrollment.objects.filter(
                student=student
            ).values_list("id", flat=True)
        )

        actual_ids = {
            item["id"] for item in results
        }

        # 当前页只有10条，检查当前页全部属于该学生
        self.assertTrue(actual_ids.issubset(expected_ids))

    def test_teacher_can_only_see_own_course_enrollments(self):
        teacher_user = self.teacher_users[0]
        teacher = self.teachers[0]

        self.authenticate(teacher_user)

        response = self.client.get("/api/enrollments/")

        results = self.get_results(response)

        expected_ids = set(
            Enrollment.objects.filter(
                course__teacher=teacher
            ).values_list("id", flat=True)
        )

        actual_ids = {
            item["id"] for item in results
        }

        self.assertEqual(response.data["count"], 30)
        self.assertTrue(actual_ids.issubset(expected_ids))

    def test_admin_can_see_all_enrollments(self):
        self.authenticate(self.admin)

        response = self.client.get("/api/enrollments/")

        self.get_results(response)

        self.assertEqual(response.data["count"], 60)
