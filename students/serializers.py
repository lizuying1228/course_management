from rest_framework import serializers
from students.models import Student

class StudentSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    student_no = serializers.CharField(required=True)
    class Meta:
        model = Student
        fields = ["id", "user", "name", "student_no", "age"]

        read_only_fields = ["id", "user"]

    def validate_age(self, value):
        if value < 1:
            raise serializers.ValidationError("年龄必须大于等于 1")
        return value

    def validate_student_no(self, value):
        queryset = Student.objects.filter(student_no = value)

        #更新对象时排除自己
        if self.instance:
            queryset = queryset.exclude(pk = self.instance.pk)

        if queryset.exists():
            raise serializers.ValidationError("该学号已存在")
        
        return value