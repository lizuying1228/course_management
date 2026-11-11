from django.urls import path
from users.views import (StudentRegisterView, TeacherRegisterView, 
                         LoginView, LogoutView, CurrentView)

urlpatterns = [
    path('register/student/', StudentRegisterView.as_view(), name = 'student-register'),
    path('register/teacher/', TeacherRegisterView.as_view(), name = 'teacher-register'),
    path('login/',LoginView.as_view(), name = 'login'),
    path('logout/', LogoutView.as_view(), name = 'logout'),
    path('me/', CurrentView.as_view(), name = 'current-user')
]