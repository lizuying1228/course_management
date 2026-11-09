from django.contrib import admin
from teachers.models import Teacher
from courses.models import Course
# Register your models here.

class CourseInline(admin.TabularInline):
    model = Course
    extra = 1

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "department"]
    search_fields = ["name", "department"]
    list_filter = ["department"]
    ordering = ["id"]
    
    inlines = [CourseInline]
