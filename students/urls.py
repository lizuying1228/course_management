from django.urls import path
from students.views import StudentListAPIView
from students.views import StudentDetailAPIView

urlpatterns = [
    path('', StudentListAPIView.as_view(), name = "student-list"),
    path('<int:pk>/', StudentDetailAPIView.as_view(), name = "student-detail")
]