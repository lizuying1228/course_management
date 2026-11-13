import django_filters
from courses.models import Course

class CourseFilter(django_filters.FilterSet):

    teacher = django_filters.NumberFilter(field_name="teacher", lookup_expr="exact")

    class Meta:
        model = Course
        fields = ["is_active", "capacity"]