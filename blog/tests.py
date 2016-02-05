from django.test import TestCase
from django.contrib.auth import get_user_model
from . import models

# Create your tests here.
class TestProfileModel(TestCase):
    def test_profile_creation(self):
        User = get_user_model()
        user = User.objects.create(username="alexander980", password="Integration69")
        self.assertIsInstance(user.profile, models.UserProfile)
        user.save()
        self.assertIsInstance(user.profile, models.UserProfile)
