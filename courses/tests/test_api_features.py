
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient

from teachers.models import Teacher
from courses.models import Course


class CourseAPIFeaturesTest(APITestCase):

    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="admin",
            password="password123",
            email="admin@example.com",
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)

        self.teacher_user = User.objects.create_user(
            username="teacher",
            password="password123",
        )

        self.teacher = Teacher.objects.create(
            user=self.teacher_user,
            name="Python Mentor",
            department="Computer Science",
        )

        self.other_teacher_user = User.objects.create_user(
            username="other_teacher",
            password="password123",
        )

        self.other_teacher = Teacher.objects.create(
            user=self.other_teacher_user,
            name="Java Mentor",
            department="Engineering",
        )

        # 创建60门课程，用于测试分页和最大页大小
        self.courses = []

        for i in range(60):
            teacher = self.teacher if i % 2 == 0 else self.other_teacher

            course = Course.objects.create(
                teacher=teacher,
                title=f"Python Course {i:02d}" if i % 2 == 0
                      else f"Java Course {i:02d}",
                description=f"Backend Course {i}",
                capacity=30 if i % 3 == 0 else 20,
                is_active=i % 2 == 0,
            )

            self.courses.append(course)

    def get_results(self, response):
        self.assertEqual(response.status_code, 200)
        self.assertIn("results", response.data)
        return response.data["results"]

    # -------------------------
    # 一、过滤测试
    # -------------------------

    def test_filter_by_is_active(self):
        response = self.client.get(
            "/api/courses/?is_active=true"
        )

        results = self.get_results(response)

        self.assertGreater(len(results), 0)

        for item in results:
            self.assertTrue(item["is_active"])

    def test_filter_by_teacher(self):
        response = self.client.get(
            f"/api/courses/?teacher={self.teacher.id}"
        )

        self.get_results(response)

        expected_count = Course.objects.filter(
            teacher=self.teacher
        ).count()

        self.assertEqual(response.data["count"], expected_count)

    def test_filter_by_capacity(self):
        response = self.client.get(
            "/api/courses/?capacity=30"
        )

        results = self.get_results(response)

        self.assertGreater(len(results), 0)

        for item in results:
            self.assertEqual(item["capacity"], 30)

    # -------------------------
    # 二、搜索测试
    # -------------------------

    def test_search_by_title(self):
        response = self.client.get(
            "/api/courses/?search=Python"
        )

        results = self.get_results(response)

        self.assertGreater(response.data["count"], 0)

        for item in results:
            self.assertIn("Python", item["title"])

    def test_search_by_teacher_name(self):
        response = self.client.get(
            "/api/courses/?search=Python Mentor"
        )

        self.get_results(response)

        expected_count = Course.objects.filter(
            teacher__name__icontains="Python Mentor"
        ).count()

        self.assertEqual(response.data["count"], expected_count)

    # -------------------------
    # 三、排序测试
    # -------------------------

    def test_ordering_by_title(self):
        response = self.client.get(
            "/api/courses/?ordering=title"
        )

        results = self.get_results(response)

        actual_ids = [item["id"] for item in results]

        expected_ids = list(
            Course.objects.order_by("title").values_list(
                "id", flat=True
            )[:10]
        )

        self.assertEqual(actual_ids, expected_ids)

    def test_ordering_by_capacity_desc(self):
        response = self.client.get(
            "/api/courses/?ordering=-capacity"
        )

        results = self.get_results(response)

        capacities = [item["capacity"] for item in results]

        self.assertEqual(capacities, sorted(capacities, reverse=True))

    # -------------------------
    # 四、分页测试
    # -------------------------

    def test_default_pagination(self):
        response = self.client.get("/api/courses/")

        results = self.get_results(response)

        self.assertEqual(response.data["count"], 60)
        self.assertEqual(len(results), 10)

    def test_second_page(self):
        response1 = self.client.get(
            "/api/courses/?page=1"
        )

        response2 = self.client.get(
            "/api/courses/?page=2"
        )

        results1 = self.get_results(response1)
        results2 = self.get_results(response2)

        ids1 = {item["id"] for item in results1}
        ids2 = {item["id"] for item in results2}

        self.assertEqual(len(results1), 10)
        self.assertEqual(len(results2), 10)
        self.assertTrue(ids1.isdisjoint(ids2))

    def test_custom_page_size(self):
        response = self.client.get(
            "/api/courses/?page_size=20"
        )

        results = self.get_results(response)

        self.assertEqual(len(results), 20)

    def test_max_page_size(self):
        response = self.client.get(
            "/api/courses/?page_size=100"
        )

        results = self.get_results(response)

        self.assertEqual(len(results), 50)

    # -------------------------
    # 五、组合测试
    # -------------------------

    def test_filter_search_ordering_pagination_together(self):
        response = self.client.get(
            "/api/courses/"
            "?is_active=true"
            "&capacity=30"
            "&search=Python"
            "&ordering=title"
            "&page=1"
            "&page_size=5"
        )

        results = self.get_results(response)

        self.assertGreater(response.data["count"], 0)
        self.assertLessEqual(len(results), 5)

        for item in results:
            self.assertTrue(item["is_active"])
            self.assertEqual(item["capacity"], 30)

        titles = [item["title"] for item in results]

        self.assertEqual(titles, sorted(titles))
