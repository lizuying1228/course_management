from rest_framework import serializers
from courses.models import Course

class CourseSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=True)

    class Meta:
        model = Course
        fields = ["id", "teacher", "title", "description", 
                  "capacity", "is_active", "created_at", "updated_at"]

        read_only_fields = ["id", "created_at", "updated_at", "teacher"]

    def validate_capacity(self, value):
        if value < 1:
            raise serializers.ValidationError("容量必须大于等于 1")
        return value

    def validate_title(self, value):
        if not value.strip():
            raise serializers.ValidationError("课程名不能为空")
        return value
    
    #is_active需要有权限的人才能更改
