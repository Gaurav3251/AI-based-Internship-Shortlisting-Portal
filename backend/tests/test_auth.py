from django.test import TestCase
from django.contrib.auth import get_user_model


class AuthTests(TestCase):
    def test_create_user(self):
        User = get_user_model()
        user = User.objects.create_user(email='u@college_name.org', password='pass1234', role='student')
        self.assertEqual(user.email, 'u@college_name.org')
