from rest_framework import serializers
from teachers.models import Teacher
from django.contrib.auth.models import User

class TeacherSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    account_active = serializers.BooleanField(source="user.is_active", read_only=True)

    class Meta:
        model = Teacher
        fields = ["id", "user", "username", "account_active", "name", "department"]

        read_only_fields = ["id", "user"]

    def validate_name(self, value):
        if not value.strip(): 
            raise serializers.ValidationError("姓名不能为空")
        return value


    