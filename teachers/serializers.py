from rest_framework import serializers
from teachers.models import Teacher
from django.contrib.auth.models import User

class TeacherSerializer(serializers.ModelSerializer):

    class Meta:
        model = Teacher
        fields = ["id", "user", "name", "department"]

        read_only_fields = ["id", "user"]

    def validate_name(self, value):
        if not value.strip(): 
            raise serializers.ValidationError("姓名不能为空")
        return value


    