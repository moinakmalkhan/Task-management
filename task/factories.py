import factory
from task.models import Task
from django.conf import settings
import pytz


class TaskFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Task

    name = factory.Faker("name")
    description = factory.Faker("text")
    deadline = factory.Faker(
        "date_time_between",
        start_date="-1y",
        end_date="+1y",
        tzinfo=pytz.timezone(settings.TIME_ZONE),
    )  # noqa
    created_by = factory.SubFactory("account.factories.UserFactory")
    type = factory.Faker("random_element", elements=Task.TASK_TYPES)
    duration = factory.Faker("random_element", elements=Task.TASK_DUERATIONS)
    score = factory.Faker("random_int", min=1, max=10)
    is_completed = factory.Faker("boolean")
