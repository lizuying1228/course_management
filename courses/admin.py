from django.contrib import admin
from courses.models import Course
# Register your models here.
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "teacher", "capacity", "is_active"]
    search_fields = ["title", "description"]
    list_filter = ["is_active", "teacher"]
    ordering = ["id"]