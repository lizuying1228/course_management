from django.db import models
from students.models import Student
from courses.models import Course
# Create your models here.
class Enrollment(models.Model):
    student = models.ForeignKey(Student, 
                                on_delete = models.CASCADE, related_name = "enrollments")
    course = models.ForeignKey(Course, on_delete = models.PROTECT, related_name = "enrollments")
    enrolled_at = models.DateTimeField(auto_now_add = True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields = ["student", "course"],
                name = "unique_student_course"
            )
        ]

        verbose_name = "课程记录"
        verbose_name_plural = "课程记录"

    def __str__(self) -> str:
        return f"{self.student} -> {self.course}"