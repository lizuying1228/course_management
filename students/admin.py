from django.contrib import admin
from students.models import Student
# Register your models here.
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "student_no", "age"]
    search_fields = ["name", "student_no"]
    list_filter = ["age"]
    ordering = ["id"]