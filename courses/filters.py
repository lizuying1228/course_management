import django_filters
from courses.models import Course

class CourseFilter(django_filters.FilterSet):

    teacher = django_filters.NumberFilter(field_name="teacher", lookup_expr="exact")
    code = django_filters.CharFilter(field_name="code", lookup_expr="iexact")

    class Meta:
        model = Course
        fields = ["is_active", "capacity", "code"]