from rest_framework.routers import DefaultRouter
from enrollments.views import EnrollmentView

router = DefaultRouter()
router.register(
    r"enrollments",
    EnrollmentView,
    basename = "enrollment"
)

urlpatterns = router.urls