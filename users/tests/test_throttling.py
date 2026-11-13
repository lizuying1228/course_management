from django.contrib.auth.models import User
from django.core.cache import cache
from rest_framework.test import APITestCase, APIClient


class ThrottlingTest(APITestCase):

    def setUp(self):
        cache.clear()

        self.user = User.objects.create_superuser(
            username="throttle_user",
            password="password123"
        )

    # def test_anonymous_user_throttle(self):
    #     client = APIClient()

    #     response = None

    #     for _ in range(21):
    #         response = client.get("/api/courses/")

    #     self.assertEqual(response.status_code, 429)

    def test_authenticated_user_throttle(self):
        client = APIClient()
        client.force_authenticate(user=self.user)

        response = None

        for _ in range(121):
            response = client.get("/api/courses/")

        self.assertEqual(response.status_code, 429)