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
            
class StudentModelView(ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        data = self.request.data
        if not isinstance(data, dict):
            raise ValidationError({"request": "请求必须是JSON格式"})

        user_id = data.get("user_id")

        if not user_id:
            raise ValidationError({"user_id": "必须提供user_id"})

        if int(user_id) <= 0:
            raise ValidationError({"user_id": "user_id必须大于 0"})

        user = get_object_or_404(User, pk = int(user_id))

        student = Student.objects.filter(user = user)
        if student:
            raise ValidationError({"user_id": "该用户已被绑定"})

        serializer.save(user = user)

    def get_queryset(self):
        if self.action == "list":
            return Student.objects.select_related("user")

        if self.action == "retrieve":
            return Student.objects.select_related("user")

        return Student.objects.all()
