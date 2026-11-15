from rest_framework import serializers
from enrollments.models import Enrollment
from students.models import Student
from courses.models import Course
from students.serializers import StudentSerializer
from courses.serializers import CourseSerializer

class EnrollmentSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    course = CourseSerializer(read_only=True)

    class Meta:
        model = Enrollment
        fields = [
            "id",
            "student",
            "course",
            "enrolled_at",
        ]

class EnrollmentCreateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    enrolled_at = serializers.DateTimeField(read_only=True)
    course_id = serializers.IntegerField(write_only=True, min_value = 1)

    #student只读没实现，后续从登陆用户获取学生信息
    #course从客户端接收课程
    #验证课程存在
    #不允许选停用的课

    class Meta:
        model = Enrollment
        fields = ["id", "course_id", "enrolled_at"]

    def validate_course_id(self, value):
        try:
            course = Course.objects.get(pk = value)
        except Course.DoesNotExist:
            raise serializers.ValidationError("该课程不存在")

        if not course.is_active:
            raise serializers.ValidationError("该课程未开放")

        return value

    def validate(self, attrs):
        # 2. 验证当前学生是否重复选课（把防重移到这里，错误就会准确挂载到 "course" 字段上）
        if "student_id" in self.initial_data:
            raise serializers.ValidationError({
                "student_id": "不能自行指定学生，学生身份由登录用户决定"
        })

        student = self.context.get("student")

        if student is None:
            raise serializers.ValidationError("缺少学生信息")

        course_id = attrs.get("course_id")

        course = Course.objects.get(pk=course_id)

        exists = Enrollment.objects.filter(student = student, course = course)

        if exists:
            raise serializers.ValidationError({"course": "该学生已经选过这门课"})

        return attrs   

    def create(self, validated_data):
        return Enrollment.objects.create(**validated_data)

        