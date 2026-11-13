from django.contrib.auth.models import User
from django.urls import reverse

from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from teachers.models import Teacher
from courses.models import Course


class CourseFilterAPITest(APITestCase):

    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin",
            password="password123",
            is_staff=True,
        )

        self.teacher_user1 = User.objects.create_user(
            username="teacher1",
            password="password123",
        )

        self.teacher_user2 = User.objects.create_user(
            username="teacher2",
            password="password123",
        )

        self.teacher1 = Teacher.objects.create(
            user=self.teacher_user1,
            name="Alice Teacher",
            department="Computer Science",
        )

        self.teacher2 = Teacher.objects.create(
            user=self.teacher_user2,
            name="Bob Teacher",
            department="Mathematics",
        )

        self.course1 = Course.objects.create(
            teacher=self.teacher1,
            title="Python Basic",
            description="Python introduction",
            capacity=30,
            is_active=True,
        )

        self.course2 = Course.objects.create(
            teacher=self.teacher1,
            title="Django Advanced",
            description="Django development",
            capacity=20,
            is_active=True,
        )

        self.course3 = Course.objects.create(
            teacher=self.teacher2,
            title="CUDA Programming",
            description="GPU programming",
            capacity=40,
            is_active=False,
        )

        self.url = reverse("course-list")

        self.authenticate(self.admin)

    def authenticate(self, user):
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {token.key}"
        )

    def get_ids(self, response):
        self.assertEqual(response.status_code, 200)
        return [
            item["id"]
            for item in response.data["results"]
        ]

    # 1. 根据课程开放状态过滤
    def test_filter_by_is_active(self):
        response = self.client.get(
            self.url,
            {"is_active": "true"},
        )

        ids = self.get_ids(response)

        self.assertEqual(
            set(ids),
            {self.course1.id, self.course2.id},
        )

    # 2. 根据教师 ID 过滤
    def test_filter_by_teacher(self):
        response = self.client.get(
            self.url,
            {"teacher": self.teacher1.id},
        )

        ids = self.get_ids(response)

        self.assertEqual(
            set(ids),
            {self.course1.id, self.course2.id},
        )

    # 3. 多个过滤条件组合
    def test_multiple_filters(self):
        response = self.client.get(
            self.url,
            {
                "is_active": "true",
                "teacher": self.teacher1.id,
            },
        )

        ids = self.get_ids(response)

        self.assertEqual(
            set(ids),
            {self.course1.id, self.course2.id},
        )

    # 4. 根据课程标题搜索
    def test_search_by_title(self):
        response = self.client.get(
            self.url,
            {"search": "Python"},
        )

        ids = self.get_ids(response)

        self.assertEqual(ids, [self.course1.id])

    # 5. 根据课程描述搜索
    def test_search_by_description(self):
        response = self.client.get(
            self.url,
            {"search": "GPU"},
        )

        ids = self.get_ids(response)

        self.assertEqual(ids, [self.course3.id])

    # 6. 根据教师姓名搜索
    def test_search_by_teacher_name(self):
        response = self.client.get(
            self.url,
            {"search": "Alice Teacher"},
        )

        ids = self.get_ids(response)

        self.assertEqual(
            set(ids),
            {self.course1.id, self.course2.id},
        )

    # 7. 课程容量升序
    def test_ordering_capacity_ascending(self):
        response = self.client.get(
            self.url,
            {"ordering": "capacity"},
        )

        ids = self.get_ids(response)

        self.assertEqual(
            ids,
            [
                self.course2.id,
                self.course1.id,
                self.course3.id,
            ],
        )

    # 8. 课程容量降序
    def test_ordering_capacity_descending(self):
        response = self.client.get(
            self.url,
            {"ordering": "-capacity"},
        )

        ids = self.get_ids(response)

        self.assertEqual(
            ids,
            [
                self.course3.id,
                self.course1.id,
                self.course2.id,
            ],
        )

    # 9. 非法排序字段不能生效
    def test_invalid_ordering_field(self):
        response = self.client.get(
            self.url,
            {"ordering": "teacher__user__password"},
        )

        ids = self.get_ids(response)

        # 非允许字段会被忽略，使用默认排序
        self.assertEqual(
            ids,
            [
                self.course1.id,
                self.course2.id,
                self.course3.id,
            ],
        )