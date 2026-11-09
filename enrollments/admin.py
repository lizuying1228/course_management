from django.contrib import admin
from enrollments.models import Enrollment
# Register your models here.
@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ["id", "student", "course", "enrolled_at"]
    search_fields = ["student__name", "course__title"]
    list_filter = ["enrolled_at"]
    ordering = ["id"]