from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from courses.models import Course
from courses.serializers import CourseSerializer
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from teachers.models import Teacher
from django.db.models.deletion import ProtectedError

# Create your views here.
class CourseListView(ListCreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        if not isinstance(request.data, dict):
            return Response({"Error": "请求对象必须是JSON对象！"}, status=status.HTTP_400_BAD_REQUEST)

        teacher_id = request.data.get("teacher_id")

        if not teacher_id:
            return Response({"Error": "必须提供teacher_id"}, status=status.HTTP_400_BAD_REQUEST)

        teacher = get_object_or_404(Teacher, pk = teacher_id)

        serializer = self.get_serializer(data = request.data)

        if serializer.is_valid():
            course = serializer.save(teacher = teacher)
            return Response(CourseSerializer(course).data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CourseDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [AllowAny]

    def delete(self, request, *args, **kwargs):
        course = self.get_object()

        try:
            course.delete()
            
        except ProtectedError:
            return Response({"Error": "该课程已有学生选课，不能删除"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)