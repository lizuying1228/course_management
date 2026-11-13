from enrollments.models import Enrollment
import django_filters

class EnrolllmentFilter(django_filters.FilterSet):
    class Meta:
        model = Enrollment
        fields = ["course", "student"]