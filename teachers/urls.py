from django.urls import path
from rest_framework.routers import DefaultRouter
from teachers.views import TeacherModelView

router = DefaultRouter()

router.register(
    r"teachers",
    TeacherModelView,
    basename = "teacher"
)

urlpatterns = router.urls

