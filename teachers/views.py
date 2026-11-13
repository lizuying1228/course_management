from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import (ListModelMixin, CreateModelMixin, 
                                   RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin)
from teachers.models import Teacher
from teachers.serializers import TeacherSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

# Create your views here.
# class TeacherListView(ListModelMixin, CreateModelMixin, GenericAPIView):
#     queryset = Teacher.objects.all()
#     serializer_class = TeacherSerializer
#     permission_classes = [AllowAny]

#     def get(self, request, *args, **kwargs):
#         return self.list(request, *args, **kwargs)

#     def post(self, request):
#         if not isinstance(request.data, dict):
#             return Response(
#                 {"error": "请求数据必须是 JSON 对象"},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         user_id = request.data.get("user_id")

#         if not user_id:
#             return Response({"Error": "需要提供user_id"}, status=status.HTTP_400_BAD_REQUEST)

#         user = get_object_or_404(User, pk=user_id)

#         if Teacher.objects.filter(user = user).exists():
#             return Response({"error": "该用户已经关联学生资料"}, status=status.HTTP_400_BAD_REQUEST)
        
#         serializer = TeacherSerializer(data = request.data)

#         if serializer.is_valid():
#             teacher = serializer.save(user = user)
#             return Response(TeacherSerializer(teacher).data, status = status.HTTP_201_CREATED)
#         return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)


# class TeacherDetailView(RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, GenericAPIView):
    # queryset = Teacher.objects.all()
    # serializer_class = TeacherSerializer
    # permission_classes = [AllowAny]

    # def get(self, request, *args, **kwargs):
    #     return self.retrieve(request, *args, **kwargs)

    # def put(self, request, *args, **kwargs):
    #     return self.update(request, *args, **kwargs)

    # def patch(self, request, *args, **kwargs):
    #     return self.partial_update(request, *args, **kwargs)

    # def delete(self, request, *args, **kwargs):
    #     return self.destroy(request, *args, **kwargs)

from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import ValidationError
from users.permissions import Teacherpermission, is_student, is_teacher, is_admin
from teachers.pagination import TeacherPagination

class TeacherModelView(ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    permission_classes = [Teacherpermission]
    pagination_class = TeacherPagination

    def get_queryset(self):
        user = self.request.user

        if is_admin(user) or is_teacher(user) or is_student(user):
            return Teacher.objects.select_related("user").order_by("id")

        return Teacher.objects.none()

    def perform_create(self, serializer):
        user = self.request.user

        if not is_admin(user):
            raise ValidationError(
                "只有管理员可以创建教师资料"
            )

        data = self.request.data

        if not isinstance(data, dict):
            raise ValidationError({
                "error": "请求数据必须是 JSON 对象"
            })

        user_id = data.get("user_id")

        if user_id is None:
            raise ValidationError({
                "user_id": "必须提供 user_id"
            })

        try:
            user_id = int(user_id)
        except (TypeError, ValueError):
            raise ValidationError({
                "user_id": "user_id 必须是有效整数"
            })

        if user_id <= 0:
            raise ValidationError({
                "user_id": "user_id 必须大于 0"
            })

        target_user = get_object_or_404(
            User,
            pk=user_id
        )

        if Teacher.objects.filter(user=target_user).exists():
            raise ValidationError({
                "user_id": "该用户已经拥有教师资料"
            })

        if hasattr(target_user, "student"):
            raise ValidationError({
                "user_id": "该用户已经是学生，不能再创建教师资料"
            })

        serializer.save(user=target_user)


        