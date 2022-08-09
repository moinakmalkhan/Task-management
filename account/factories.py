from django.contrib.auth import get_user_model
import factory
from account.models import UserProfile


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    username = factory.Sequence(lambda n: "user{}".format(n))
    password = factory.PostGenerationMethodCall("set_password", "password")
    email = factory.Faker("email")


class UserProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserProfile

    user = factory.SubFactory(UserFactory)
    phone = factory.Faker("phone_number")
