from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
# Create your models here.
class Student(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, 
                                on_delete = models.CASCADE, related_name = "student")
    name = models.CharField(max_length = 50)
    student_no = models.CharField(max_length = 50, unique = True)
    age = models.PositiveIntegerField(validators = [MinValueValidator(1)])

    def __str__(self) -> str:
        return f"{self.name}"
