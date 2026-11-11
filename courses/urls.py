from django.urls import path
from rest_framework.routers import DefaultRouter
from courses.views import CourseModelView

router = DefaultRouter()
router.register(
    r"courses",
    CourseModelView,
    basename = "course"
)

urlpatterns = router.urls