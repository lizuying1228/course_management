from rest_framework import serializers
from enrollments.models import Enrollment
from students.models import Student
from courses.models import Course

class EnrollmentSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    enrolled_at = serializers.DateTimeField(read_only=True)
    student = serializers.PrimaryKeyRelatedField(read_only=True)

    #student只读没实现，后续从登陆用户获取学生信息
    #course从客户端接收课程
    #验证课程存在
    #不允许选停用的课

    class Meta:
        model = Enrollment
        fields = ["id", "student", "course", "enrolled_at"]


    def validate_course(self, value):
        # 1. 验证课程是否停用
        if not value.is_active:
            raise serializers.ValidationError("该课程没有开放选课")

        # 2. 验证当前学生是否重复选课（把防重移到这里，错误就会准确挂载到 "course" 字段上）
        student = self.context.get("student")

        if student is not None:
            exists = Enrollment.objects.filter(
                student=student, course=value
            ).exists()

        # 更新时排除自身
        if self.instance:
            exists = (
                Enrollment.objects.filter(student=student, course=value)
                .exclude(pk=self.instance.pk)
                .exists()
            )

        if exists:
            raise serializers.ValidationError("该学生已经选过这门课")

        return value

    def validate(self, attrs):

        student = self.context.get("student")

        if student is None:
            raise serializers.ValidationError("缺少学生信息")

        return attrs

    def create(self, validated_data):
        student = self.context.get("student")

        if student is None:
            raise serializers.ValidationError("缺少当前学生信息")

        return Enrollment.objects.create(student = student, **validated_data)

        