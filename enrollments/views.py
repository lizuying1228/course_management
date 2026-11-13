from django.shortcuts import render, get_object_or_404
from students.models import Student
from courses.models import Course
from enrollments.models import Enrollment
from users.permissions import is_admin, is_student, is_teacher
from rest_framework import mixins, viewsets
from enrollments.serializers import EnrollmentSerializer, EnrollmentCreateSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError, PermissionDenied
from django.db import transaction, IntegrityError
from enrollments.filters import EnrolllmentFilter
from enrollments.pagination import EnrollmentPagination

# Create your views here.
class EnrollmentView(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
    ):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = EnrolllmentFilter
    search_fields = ["student__name", "student__student_no", "course__title"]
    ordering_fields = ["enrolled_at", "student__name", "course__title"]
    ordering = ["-enrolled_at"]
    pagination_class = EnrollmentPagination
    throttle_scope = "enroll"

    def get_queryset(self):
        user = self.request.user
        queryset =  Enrollment.objects.select_related(
                    "student", 
                    "student__user", 
                    "course",
                    "course__teacher",
                    "course__teacher__user"
                ).order_by("id")

        if is_admin(user):
            return queryset

        elif is_teacher(user):
            return queryset.filter(course__teacher__user = user)

        elif is_student(user):
            return queryset.filter(student__user = user)

        else:
            raise PermissionDenied("该用户没有权限查看")

    def get_serializer_class(self):
        if self.action == "create":
            return EnrollmentCreateSerializer
        return EnrollmentSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        user = self.request.user
        if is_student(user):
            context["student"] = user.student
        else:
            context["student"] = None
        return context

    def perform_create(self, serializer):
        user = self.request.user
        if not is_student(user):
            raise PermissionError("只有学生可以选课")

        student = user.student
        course_id = serializer.validated_data["course_id"]
        try:
            with transaction.atomic():
                course = get_object_or_404(Course.objects.select_for_update(), pk = course_id)

                if not course.is_active:
                    raise ValidationError("该课程没有开放")

                exists = Enrollment.objects.filter(student = student, course = course).exists()
                if exists:
                    raise ValidationError("已选择该课程")

                count = Enrollment.objects.filter(course = course).count()
                if count >= course.capacity:
                    raise ValidationError("该课程人数已满")

                serializer.save(student = student, course = course)

        except IntegrityError:
            raise ValidationError("重复选课")

    def perform_destroy(self, instance):
        user = self.request.user
        if is_admin(user):
            instance.delete()
            return 

        if is_teacher(user):
            raise PermissionDenied("教师无权退选学生课程")

        if is_student(user):
            if instance.student.user_id != user.id:
                raise PermissionDenied("不允许退选他人课程")

            instance.delete()
            return

        raise PermissionDenied("无权限")


        
           

        
        
        
        