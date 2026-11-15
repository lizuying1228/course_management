from rest_framework import serializers
from courses.models import Course

class CourseSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=True)
    enrollment_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Course
        fields = ["id", "code", "teacher", "title", "description",
                  "capacity", "is_active", "enrollment_count", "created_at", "updated_at"]

        read_only_fields = ["id", "code", "created_at", "updated_at", "teacher", "enrollment_count"]

    def validate_capacity(self, value):
        if value < 1:
            raise serializers.ValidationError("容量必须大于等于 1")
        return value

    def validate_title(self, value):
        if not value.strip():
            raise serializers.ValidationError("课程名不能为空")
        return value
    
    #is_active需要有权限的人才能更改
