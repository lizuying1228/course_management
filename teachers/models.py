from django.db import models
from django.conf import settings
# Create your models here.
class Teacher(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, 
                                on_delete = models.CASCADE, related_name = "teacher")
    name = models.CharField(max_length = 50)
    department = models.CharField(max_length = 100, blank = True)

    class Meta:
        verbose_name = "教师"
        verbose_name_plural = "教师"
        
    def __str__(self) -> str:
        return f"{self.name}"