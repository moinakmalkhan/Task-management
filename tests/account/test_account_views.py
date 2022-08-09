from django.urls import reverse
from django.test.testcases import TestCase
from django.contrib.auth import get_user_model
from account.factories import UserProfileFactory, UserFactory
from account.forms import SignUpForm, LoginFrom

User = get_user_model()


class TestSignUpView(TestCase):
    def setUp(self) -> None:
        self.VALID_POST_DATA = {
            "first_name": "test",
            "last_name": "test",
            "email": "test1@gmail.com",
            "password": "test123",
            "password_confirm": "test123",
            "phone": "1234567890",
        }

        self.url = reverse("account:signup")

    def test_get(self):
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, "account/signup.html")
        self.assertTrue(hasattr(res.context["form"], "request"))
        self.assertEqual(res.context["form"].__class__, SignUpForm)

    def test_post_with_valid_data(self):
        data = self.VALID_POST_DATA.copy()
        res = self.client.post(self.url, data)
        self.assertEqual(res.status_code, 302)
        self.assertEqual(User.objects.count(), 1)
        user = User.objects.get(email=data["email"])
        self.assertEqual(user.first_name, data["first_name"])
        self.assertEqual(user.last_name, data["last_name"])
        self.assertEqual(user.email, data["email"])
        self.assertEqual(user.user_profile.phone, data["phone"])
        assert res.cookies["sessionid"]

    def test_post_with_invalid_email(self):
        data = self.VALID_POST_DATA.copy()
        data["email"] = "test"
        res = self.client.post(self.url, data)
        self.assertEqual(
            res.context["form"].errors["email"], ["Enter a valid email address."]
        )
        self.assertEqual(res.status_code, 200)

    def test_post_with_already_exists_email(self):
        data = self.VALID_POST_DATA.copy()
        res = self.client.post(self.url, data)
        self.assertEqual(User.objects.count(), 1)
        res = self.client.post(self.url, data)
        self.assertEqual(res.context["form"].errors["email"], ["Email already exists."])
        self.assertEqual(res.status_code, 200)
        self.assertEqual(User.objects.count(), 1)

    def test_post_with_already_exists_phone(self):
        data = self.VALID_POST_DATA.copy()
        res = self.client.post(self.url, data)
        self.assertEqual(res.status_code, 302)
        self.assertEqual(User.objects.count(), 1)
        data["email"] = "test2@gmail.com"
        res = self.client.post(self.url, data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context["form"].errors["phone"], ["Phone already exists."])
        data["phone"] = ""
        res = self.client.post(self.url, data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(
            res.context["form"].errors["phone"], ["This field is required."]
        )
        self.assertEqual(User.objects.count(), 1)

    def test_post_with_already_exists_wrong_password(self):
        data = self.VALID_POST_DATA.copy()
        data["email"] = "test2@gmail.com"
        data["password"] = "wrong"
        res = self.client.post(self.url, data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(
            res.context["form"].errors["password"], ["Passwords do not match."]
        )
        self.assertEqual(User.objects.count(), 0)


class TestLoginView(TestCase):
    def setUp(self) -> None:
        self.VALID_EMAIL = "test@gmail.com"
        self.VALID_PASSWORD = "test"
        self.VALID_PHONE = "12345678"
        user = UserFactory(
            email=self.VALID_EMAIL,
            password=self.VALID_PASSWORD,
        )
        self.url = reverse("account:login")
        UserProfileFactory(user=user, phone=self.VALID_PHONE)

    def test_get(self):
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, "account/login.html")
        self.assertTrue(hasattr(res.context["form"], "request"))
        self.assertEqual(res.context["form"].__class__, LoginFrom)

    def test_post_with_email(self):
        data = {"email": self.VALID_EMAIL, "password": self.VALID_PASSWORD}
        res = self.client.post(self.url, data)
        self.assertEqual(res.status_code, 302)
        assert res.cookies["sessionid"]

    def test_post_with_phone(self):
        data = {"email": self.VALID_PHONE, "password": self.VALID_PASSWORD}
        res = self.client.post(self.url, data)
        self.assertEqual(res.status_code, 302)

    def test_post_with_invalid_data(self):
        data = {"email": "incorrect", "password": self.VALID_PASSWORD}
        res = self.client.post(self.url, data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(
            res.context["form"].errors["email"], ["Incorrect email or password."]
        )
        data = {"email": self.VALID_EMAIL, "password": "incorrect"}
        res = self.client.post(self.url, data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(
            res.context["form"].errors["email"], ["Incorrect email or password."]
        )
        data = {"email": "incorrect", "password": "incorrect"}
        res = self.client.post(self.url, data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(
            res.context["form"].errors["email"], ["Incorrect email or password."]
        )


class TestLogoutView(TestCase):
    def setUp(self) -> None:
        user = UserFactory()
        UserProfileFactory(user=user)
        self.url = reverse("account:logout")
        self.client.force_login(user)

    def test_post(self):
        res = self.client.post(self.url)
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res.url, reverse("account:login"))
