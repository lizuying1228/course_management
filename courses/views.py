from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from courses.models import Course
from courses.serializers import CourseSerializer
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from teachers.models import Teacher
from django.db.models.deletion import ProtectedError
from django.db.models import Count

# Create your views here.
# class CourseListView(ListCreateAPIView):
#     queryset = Course.objects.all()
#     serializer_class = CourseSerializer
#     permission_classes = [AllowAny]

#     def create(self, request, *args, **kwargs):
#         if not isinstance(request.data, dict):
#             return Response({"Error": "请求对象必须是JSON对象！"}, status=status.HTTP_400_BAD_REQUEST)

#         teacher_id = request.data.get("teacher_id")

#         if not teacher_id:
#             return Response({"Error": "必须提供teacher_id"}, status=status.HTTP_400_BAD_REQUEST)

#         teacher = get_object_or_404(Teacher, pk = teacher_id)

#         serializer = self.get_serializer(data = request.data)

#         if serializer.is_valid():
#             course = serializer.save(teacher = teacher)
#             return Response(CourseSerializer(course).data, status=status.HTTP_201_CREATED)
        
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class CourseDetailView(RetrieveUpdateDestroyAPIView):
#     queryset = Course.objects.all()
#     serializer_class = CourseSerializer
#     permission_classes = [AllowAny]

#     def delete(self, request, *args, **kwargs):
#         course = self.get_object()

#         try:
#             course.delete()
            
#         except ProtectedError:
#             return Response({"Error": "该课程已有学生选课，不能删除"}, status=status.HTTP_400_BAD_REQUEST)

#         return Response(status=status.HTTP_204_NO_CONTENT)

from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action
from users.permissions import Coursepermission, is_student, is_teacher, is_admin
from courses.filters import CourseFilter
from courses.pagination import CoursePagination

class CourseModelView(ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [Coursepermission]
    filterset_class = CourseFilter
    search_fields = ["code", "title", "description", "teacher__name", "=id"]
    ordering_fields = ["title", "capacity", "created_at", "updated_at"]
    ordering = ["id"]
    pagination_class = CoursePagination

    def perform_create(self, serializer):
        user = self.request.user

        if is_teacher(user):
            serializer.save(teacher = user.teacher)
            return 

        if is_admin(user):
            data = self.request.data
            if not isinstance(data, dict):
                raise ValidationError({"request": "请求必须是JSON格式"})

            teacher_id = data.get("teacher_id")
            try:
                teacher_id = int(teacher_id)
            except (TypeError, ValueError):
                raise ValidationError({"teacher_id": "teacher_id 必须是正整数"})
            if teacher_id <= 0:
                raise ValidationError({"teacher_id": "teacher_id 必须是正整数"})

            teacher = get_object_or_404(Teacher, pk=teacher_id)

            if not teacher:
                raise ValidationError({"Error": "该教师不存在"})

            serializer.save(teacher = teacher)
            return 
            
        raise ValidationError("没有创建课程的权限")

    def perform_destroy(self, instance):
        try:
            instance.delete()

        except ProtectedError:
            raise ValidationError({"Error": "该课程有学生，不能删除"})

    @action(detail = False, methods=["GET"])
    def active(self, request):
        courses = Course.objects.filter(is_active=True).annotate(
            enrollment_count=Count("enrollments")
        )
        courses = self.filter_queryset(courses)
        page = self.paginate_queryset(courses)

        if page is not None:
            # 3A. 如果开启了分页，只序列化“当前页”的数据
            serializer = self.get_serializer(page, many=True)
            # 4A. 使用 get_paginated_response 包装成标准的分页结构（带 results、count 等）
            return self.get_paginated_response(serializer.data)
        
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data, status = status.HTTP_200_OK)

    def get_queryset(self):
        user = self.request.user
        if is_admin(user) or is_teacher(user):
            return Course.objects.select_related("teacher", "teacher__user").annotate(
                enrollment_count=Count("enrollments")
            ).order_by("id")

        if is_student(user):
            return Course.objects.filter(is_active=True).select_related("teacher").annotate(
                enrollment_count=Count("enrollments")
            ).order_by("id")

        return Course.objects.none()

    

        
