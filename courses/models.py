from django.db import models
from teachers.models import Teacher
from django.core.validators import MinValueValidator
# Create your models here.
class Course(models.Model):
    teacher = models.ForeignKey(Teacher, 
                                on_delete = models.PROTECT, related_name = "courses")
    code = models.CharField(max_length=30, unique=True, blank=True)
    title = models.CharField(max_length = 100)
    description = models.TextField(blank = True)
    capacity = models.PositiveIntegerField(default = 30, 
                                           validators = [MinValueValidator(1)])
    is_active = models.BooleanField(default = True, verbose_name = "是否开放")
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

    class Meta:
        verbose_name = "课程"
        verbose_name_plural = "课程"

    def save(self, *args, **kwargs):
        creating_without_code = self.pk is None and not self.code
        super().save(*args, **kwargs)
        if creating_without_code:
            self.code = f"CRS{self.pk:05d}"
            type(self).objects.filter(pk=self.pk).update(code=self.code)

    def __str__(self) -> str:
        return f"{self.code} - {self.title}"

