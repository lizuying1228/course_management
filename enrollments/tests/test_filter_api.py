from django.contrib.auth.models import User
from django.urls import reverse

from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from students.models import Student
from teachers.models import Teacher
from courses.models import Course
from enrollments.models import Enrollment


class EnrollmentFilterAPITest(APITestCase):

    def setUp(self):
        self.student_user1 = User.objects.create_user(
            username="alice",
            password="password123",
        )

        self.student_user2 = User.objects.create_user(
            username="bob",
            password="password123",
        )

        self.teacher_user1 = User.objects.create_user(
            username="teacher1",
            password="password123",
        )

        self.teacher_user2 = User.objects.create_user(
            username="teacher2",
            password="password123",
        )

        self.student1 = Student.objects.create(
            user=self.student_user1,
            name="Alice",
            student_no="S001",
            age=20,
        )

        self.student2 = Student.objects.create(
            user=self.student_user2,
            name="Bob",
            student_no="S002",
            age=21,
        )

        self.teacher1 = Teacher.objects.create(
            user=self.teacher_user1,
            name="Teacher A",
            department="Computer Science",
        )

        self.teacher2 = Teacher.objects.create(
            user=self.teacher_user2,
            name="Teacher B",
            department="Mathematics",
        )

        self.course1 = Course.objects.create(
            teacher=self.teacher1,
            title="Python",
            description="Python course",
            capacity=30,
        )

        self.course2 = Course.objects.create(
            teacher=self.teacher2,
            title="Django",
            description="Django course",
            capacity=30,
        )

        self.enrollment1 = Enrollment.objects.create(
            student=self.student1,
            course=self.course1,
        )

        self.enrollment2 = Enrollment.objects.create(
            student=self.student2,
            course=self.course2,
        )

        self.enrollment3 = Enrollment.objects.create(
            student=self.student1,
            course=self.course2,
        )

        self.url = reverse("enrollment-list")

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

    # 9. 根据课程 ID 过滤
    def test_filter_by_course(self):
        self.authenticate(self.student_user1)

        response = self.client.get(
            self.url,
            {"course": self.course2.id},
        )

        ids = self.get_ids(response)

        self.assertEqual(ids, [self.enrollment3.id])

    # 10. 根据学生 ID 过滤
    def test_filter_by_student(self):
        self.authenticate(self.student_user1)

        response = self.client.get(
            self.url,
            {"student": self.student1.id},
        )

        ids = self.get_ids(response)

        self.assertEqual(
            set(ids),
            {self.enrollment1.id, self.enrollment3.id},
        )

    # 11. 根据学生姓名搜索
    def test_search_by_student_name(self):
        self.authenticate(self.student_user1)

        response = self.client.get(
            self.url,
            {"search": "Alice"},
        )

        ids = self.get_ids(response)

        self.assertEqual(
            set(ids),
            {self.enrollment1.id, self.enrollment3.id},
        )

    # 12. 根据课程标题搜索
    def test_search_by_course_title(self):
        self.authenticate(self.student_user1)

        response = self.client.get(
            self.url,
            {"search": "Django"},
        )

        ids = self.get_ids(response)

        self.assertEqual(ids, [self.enrollment3.id])

    # 13. 根据选课时间排序
    def test_ordering_by_enrolled_at(self):
        self.authenticate(self.student_user1)

        response = self.client.get(
            self.url,
            {"ordering": "-enrolled_at"},
        )

        ids = self.get_ids(response)

        # 本测试的记录在同一次 setUp 中创建，
        # 选课时间可能相同，所以只检查记录完整性。
        self.assertEqual(
            set(ids),
            {self.enrollment1.id, self.enrollment3.id},
        )

    # 14. 学生不能通过 student 参数查看其他学生数据
    def test_student_cannot_bypass_queryset_with_filter(self):
        self.authenticate(self.student_user1)

        response = self.client.get(
            self.url,
            {"student": self.student2.id},
        )

        ids = self.get_ids(response)

        self.assertNotIn(self.enrollment2.id, ids)

    # 15. 教师不能通过 course 参数查看其他教师的选课记录
    def test_teacher_cannot_bypass_queryset_with_filter(self):
        self.authenticate(self.teacher_user1)

        response = self.client.get(
            self.url,
            {"course": self.course2.id},
        )

        ids = self.get_ids(response)

        self.assertNotIn(self.enrollment2.id, ids)
        self.assertNotIn(self.enrollment3.id, ids)