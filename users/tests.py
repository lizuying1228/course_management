from django.test import TestCase
from django.contrib.auth.models import User
from users.serializers import UserSerializer
# Create your tests here.
class UserSerializerTest(TestCase):
    def test_create_user(self):
        data = {
            "username": "alice",
            "email": "alice@example.com",
            "password": "123456alice"
        }

        serializer = UserSerializer(data = data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

        user = serializer.save()

        self.assertEqual("alice", user.username)
        self.assertTrue(user.check_password("123456alice"))
        self.assertNotEqual("123456alice", user.password)

    def test_not_in_output(self):
        user = User.objects.create_user(username = "alice", password = "123456alice")
        serializer = UserSerializer(user)
        self.assertNotIn("password", serializer.data)

    def test_duplicate_username(self):
        User.objects.create_user(username = "alice", password = "123456alice")
        data = {
            "username": "alice",
            "password": "123456alice"
        }
        
        serializer = UserSerializer(data = data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("username", serializer.errors)

    def test_update_password(self):
        user = User.objects.create_user(username = "alice", password = "123456alice")
        data = {
            "password": "alice123456"
        }

        serializer = UserSerializer(instance = user, data = data, partial = True)

        self.assertTrue(serializer.is_valid(), serializer.errors)
        update_user = serializer.save()
        self.assertTrue(update_user.check_password("alice123456"))

