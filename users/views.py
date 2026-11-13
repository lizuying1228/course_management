from django.shortcuts import render
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from students.models import Student
from teachers.models import Teacher
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from users.serializers import (StudentRegisterSerializer, TeacherRegisterSerializer, 
                               LoginSerializer, UserInfoSerializer) 
# Create your views here.
class StudentRegisterView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = StudentRegisterSerializer(data = request.data)

        if serializer.is_valid():
            student = serializer.save()
            return Response({"message": "学生注册成功!", 
                             "user": UserInfoSerializer(student.user).data,
                             "profile": {
                                 "type": "student",
                                 "name": student.name,
                                 "student_no": student.student_no,
                                 "age": student.age
                             }}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TeacherRegisterView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = TeacherRegisterSerializer(data = request.data)

        if serializer.is_valid():
            teacher = serializer.save()
            return Response({"message": "教师注册成功!", 
                             "user": UserInfoSerializer(teacher.user).data,
                             "profile": {
                                 "type": "teacher",
                                 "name": teacher.name,
                                 "department": teacher.department
                             }}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_scope = "login"

    def post(self, request):
        serializer = LoginSerializer(data = request.data, context = {"request": request})

        if serializer.is_valid():
            user = serializer.validated_data["user"]
            token, created = Token.objects.get_or_create(user = user)
            return Response({"token": token.key,
                             "user": UserInfoSerializer(user).data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def post(self, request):
        request.auth.delete()
        return Response({"message": "退出成功！"}, status=status.HTTP_200_OK)


class CurrentView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        user = request.user
        user_data = UserInfoSerializer(user).data

        if user.is_staff or user.is_superuser:
            profile = {
                "type": "admin"
            }

        elif hasattr(user, "student"):
            student = user.student
            profile = {
                "type": "student",
                "name": student.name,
                "student_no": student.student_no,
                "age": student.age
            }

        elif hasattr(user, "teacher"):
            teacher = user.teacher
            profile = {
                "type": "teacher",
                "name":teacher.name,
                "department": teacher.department
            }

        else:
            profile = None

        return Response({**user_data, "profile": profile}, status=status.HTTP_200_OK)