from django.test.testcases import TestCase
from account.factories import UserFactory, UserProfileFactory
from django.core.exceptions import ObjectDoesNotExist
import pytest

class TestUserModel(TestCase):
    def test_pre_save(self):
        user = UserFactory()
        self.assertEqual(user.email, user.username)

    def test_user_profile(self):
        user = UserFactory()
        with pytest.raises(ObjectDoesNotExist):
            self.assertFalse(hasattr(user, 'user_profile'))
            assert user.user_profile
        UserProfileFactory(user=user)
        self.assertTrue(hasattr(user, 'user_profile'))
        self.assertEqual(user.email, user.username)
