from django.db import models
from teachers.models import Teacher
from django.core.validators import MinValueValidator
# Create your models here.
class Course(models.Model):
    teacher = models.ForeignKey(Teacher, 
                                on_delete = models.PROTECT, related_name = "courses")
    title = models.CharField(max_length = 100)
    description = models.TextField(blank = True)
    capacity = models.PositiveIntegerField(default = 30, 
                                           validators = [MinValueValidator(1)])
    is_active = models.BooleanField(default = True)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

    def __str__(self) -> str:
        return f"{self.title}"

