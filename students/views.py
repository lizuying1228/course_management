from django.shortcuts import render
from rest_framework.views import APIView
from students.models import Student
from students.serializers import StudentSerializer
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework.permissions import AllowAny

from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.db import transaction
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.authtoken.models import Token
from users.permissions import Studentpermission, is_admin, is_teacher, is_student
from students.pagination import StudentPagination
# Create your views here.
# class StudentListAPIView(APIView):
#     permission_classes = [AllowAny]

#     def get(self, request: Request) -> Response:
#         students = Student.objects.all()
#         serializer = StudentSerializer(students, many = True)
#         return Response(serializer.data, status = status.HTTP_200_OK)


#     def post(self, request: Request) -> Response:
#         if not isinstance(request.data, dict):
#             return Response(
#                 {"error": "请求数据必须是 JSON 对象"},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         user_id = request.data.get("user_id")

#         if not user_id:
#             return Response({"Error": "需要提供user_id"}, status=status.HTTP_400_BAD_REQUEST)

#         user = get_object_or_404(User, pk=user_id)

#         if Student.objects.filter(user = user).exists():
#             return Response({"error": "该用户已经关联学生资料"}, status=status.HTTP_400_BAD_REQUEST)
        
#         serializer = StudentSerializer(data = request.data)

#         if serializer.is_valid():
#             student = serializer.save(user = user)
#             return Response(StudentSerializer(student).data, status = status.HTTP_201_CREATED)
#         return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)


# class StudentDetailAPIView(APIView):
#     permission_classes = [AllowAny]

#     def get_object(self, pk: int) -> Student | None:
#         try:
#             student = Student.objects.get(id = pk)

#         except Student.DoesNotExist:
#             return None

#         return student

    
#     def get(self, request: Request, pk: int) -> Response:
#         student = self.get_object(pk)

#         if student is None:
#             return Response({"Error": "学生不存在"}, status = status.HTTP_404_NOT_FOUND)
        
#         serializer = StudentSerializer(student)
#         return Response(serializer.data, status = status.HTTP_200_OK)


#     def put(self, request: Request, pk: int) -> Response:
#         student = self.get_object(pk)

#         if student is None:
#             return Response({"Error": "学生不存在"}, status = status.HTTP_404_NOT_FOUND)

#         data = request.data
#         serializer = StudentSerializer(student, data = data)

#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status = status.HTTP_200_OK)
        
#         return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)


#     def patch(self, request: Request, pk: int) -> Response:
#         student = self.get_object(pk)

#         if student is None:
#             return Response({"Error": "学生不存在"}, status = status.HTTP_404_NOT_FOUND)

#         data = request.data
#         serializer = StudentSerializer(student, data = data, partial = True)

#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status = status.HTTP_200_OK)
        
#         return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

#     def delete(self, request: Request, pk: int) -> Response:
#         student = self.get_object(pk)

#         if student is None:
#             return Response({"Error": "学生不存在"}, status = status.HTTP_404_NOT_FOUND)

#         student.delete()
#         return Response(status = status.HTTP_204_NO_CONTENT)

from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import ValidationError
from users.permissions import Studentpermission, is_admin, is_teacher, is_student
from students.pagination import StudentPagination
            
class StudentModelView(ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [Studentpermission]
    pagination_class = StudentPagination
    search_fields = ["name", "student_no", "user__username", "=id", "=user__id"]
    ordering_fields = ["id", "name", "student_no", "age"]
    ordering = ["id"]
    filterset_fields = ["id", "student_no", "user__is_active"]

    def perform_create(self, serializer):
        if not is_admin(self.request.user):
            raise ValidationError("非管理员不可以创建学生资料")

        data = self.request.data
        if not isinstance(data, dict):
            raise ValidationError({"Error": "请求数据必须是JSON对象"})

        with transaction.atomic():
            user_id = data.get("user_id")
            if user_id is not None:
                try:
                    target_user = User.objects.get(pk=int(user_id))
                except (TypeError, ValueError):
                    raise ValidationError({"user_id": "user_id 必须是有效整数"})
                except User.DoesNotExist:
                    raise ValidationError({"user_id": "对应用户不存在"})
                if hasattr(target_user, "student"):
                    raise ValidationError({"user_id": "该用户已被绑定学生资料"})
                if hasattr(target_user, "teacher"):
                    raise ValidationError({"user_id": "该用户已是教师，不能绑定为学生"})
            else:
                username = data.get("username")
                password = data.get("password")
                if not username:
                    raise ValidationError({"username": "创建学生账号时必须提供用户名"})
                if not password or len(str(password)) < 8:
                    raise ValidationError({"password": "密码至少需要 8 位"})
                if User.objects.filter(username=username).exists():
                    raise ValidationError({"username": "该用户名已被注册"})
                target_user = User.objects.create_user(
                    username=username,
                    password=password,
                    email=data.get("email", ""),
                )

            serializer.save(user=target_user)

    def get_queryset(self):
        user = self.request.user

        if is_admin(user) or is_teacher(user):
            return Student.objects.select_related("user").order_by("id")

        if is_student(user):
            return Student.objects.filter(user = user).select_related("user")

        return Student.objects.none()

    def perform_destroy(self, instance):
        # 保留学生资料及选课历史，只停用账号并撤销旧 Token。
        user = instance.user
        user.is_active = False
        user.save(update_fields=["is_active"])
        Token.objects.filter(user=user).delete()

    @action(detail=True, methods=["post"])
    def restore(self, request, pk=None):
        """管理员恢复学生账号；学生之后重新登录即可获得新 Token。"""
        if not is_admin(request.user):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("只有管理员可以恢复学生账号")

        student = self.get_object()
        student.user.is_active = True
        student.user.save(update_fields=["is_active"])
        return Response(
            {"message": "学生账号已恢复", "student": self.get_serializer(student).data},
            status=status.HTTP_200_OK,
        )
