from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator
from students.models import Student
from django.db import transaction
from teachers.models import Teacher
from django.contrib.auth import authenticate
from rest_framework.serializers import ModelSerializer

class UserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(required=True, 
                                     validators=[UniqueValidator(queryset=User.objects.all(), message="该用户名已被注册")])

    password = serializers.CharField(write_only=True, required=True, min_length=8, trim_whitespace=False)

    class Meta:
        model = User
        fields = ["id", "username", "email", 
                  "first_name", "last_name", "password"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()

        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance


class StudentRegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100)
    password = serializers.CharField(write_only=True, min_length=8, trim_whitespace=False)
    email = serializers.EmailField(required=False, allow_blank=True)

    name = serializers.CharField(max_length=50)
    student_no = serializers.CharField(max_length=50)
    age = serializers.IntegerField(min_value=1)

    def validate_username(self, value):
        if User.objects.filter(username = value).exists():
            raise serializers.ValidationError("用户名已存在")
        return value

    def validate_student_no(self, value):
        if Student.objects.filter(student_no = value).exists():
            raise serializers.ValidationError("该学号已存在")
        return value

    @transaction.atomic
    def create(self, validated_data):
        password = validated_data.pop("password")
        username = validated_data.pop("username")
        email = validated_data.pop("email", "")

        user = User.objects.create_user(
            username = username,
            password = password,
            email = email
        )

        student = Student.objects.create(
            user = user,
            **validated_data
        )

        return student


class TeacherRegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100)
    password = serializers.CharField(write_only=True, min_length=8, trim_whitespace=False)
    email = serializers.EmailField(required=False, allow_blank=True)

    name = serializers.CharField(max_length=50)
    department = serializers.CharField(required=False, allow_blank=True, max_length=200)

    def validate_username(self, value):
        if User.objects.filter(username = value).exists():
            raise serializers.ValidationError("该用户已存在")
        return value

    @transaction.atomic
    def create(self, validated_data):
        username = validated_data.pop("username")
        password = validated_data.pop("password")
        email = validated_data.pop("email", "")

        user = User.objects.create_user(
            username = username,
            password = password,
            email = email
        )

        teacher = Teacher.objects.create(
            user = user,
            **validated_data
        )

        return teacher


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100)
    password = serializers.CharField(write_only=True, min_length=8, trim_whitespace=False)

    def validate(self, attrs):
        user = authenticate(
            request = self.context.get("request"),
            username = attrs["username"],
            password = attrs["password"]
        )

        if not user:
            raise serializers.ValidationError("用户名或密码错误")

        if not user.is_active:
            raise serializers.ValidationError("该用户已被停用")

        attrs["user"] = user

        return attrs


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]

        read_only_fields = fields

        