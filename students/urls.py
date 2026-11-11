from django.urls import path
from students.views import StudentModelView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(
    r"students", 
    StudentModelView,
    basename = "student"
)

urlpatterns = router.urls