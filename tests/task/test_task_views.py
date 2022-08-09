from django.test.testcases import TestCase
from task.forms import TaskForm
from account.factories import UserFactory, UserProfileFactory
from task.views import (
    get_redirect_url,
    get_data_to_search,
    get_field_in_search_dict,
    check_field_in_search_dict,
)
from task.models import Task
from django.urls import reverse
from task.factories import TaskFactory
from django.conf import settings
from django.utils import timezone
import random
from django.db.models import Sum


class BaseLoginRequiredTestCase(TestCase):
    def test_login_required(self):
        if self.__class__ == BaseLoginRequiredTestCase:
            return
        self.client.logout()
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 302)
        self.assertTrue(res.url.startswith(reverse(settings.LOGIN_URL)))


class TestTaskCreateView(BaseLoginRequiredTestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        UserProfileFactory(user=self.user)
        self.client.force_login(self.user)
        self.VALID_POST_DATA = {
            "name": "Test task",
            "description": "Test description",
            "deadline": "2022-01-01T00:00",
            "type": random.choice(Task.TASK_TYPES),
        }
        self.url = reverse("task:create")

    def test_get(self):
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, "task/create-task.html")
        self.assertTrue(hasattr(res.context["form"], "request"))
        self.assertEqual(res.context["form"].__class__, TaskForm)

    def test_post(self):
        data = self.VALID_POST_DATA.copy()
        res = self.client.post(self.url, data)
        self.assertEqual(res.status_code, 302)
        self.assertEqual(Task.objects.count(), 1)
        self.assertEqual(
            res.url, reverse(get_redirect_url(Task.objects.first().duration))
        )

    def test_post_with_invalid_data(self):
        data = self.VALID_POST_DATA.copy()
        data["name"] = ""
        data["description"] = ""
        data["deadline"] = ""
        data["type"] = ""
        res = self.client.post(self.url, data)
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, "task/create-task.html")
        form = res.context["form"]
        self.assertTrue(hasattr(form, "request"))
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["name"], ["This field is required."])
        self.assertEqual(form.errors["description"], ["This field is required."])
        self.assertEqual(form.errors["deadline"], ["This field is required."])
        self.assertEqual(form.errors["type"], ["This field is required."])

    def test_utils_function(self):
        self.assertEqual(
            get_data_to_search({"type": "anything", "extra_data": "anything"}),
            {"type": "anything"},
        )
        self.assertEqual(
            get_data_to_search({"type": "anything", "duration": "anything"}),
            {"type": "anything", "duration": "anything"},
        )  # noqa
        self.assertEqual(
            get_data_to_search(
                {"type": "anything", "duration": "anything"}, ["duration"]
            ),
            {"type": "anything"},
        )  # noqa
        self.assertTrue(
            check_field_in_search_dict("duration", {"duration__gt": "anything"})
        )
        self.assertFalse(check_field_in_search_dict("duration", {"type": "anything"}))
        self.assertEqual(
            get_field_in_search_dict("duration", {"duration__gt": "anything"}),
            "anything",
        )
        self.assertEqual(
            get_field_in_search_dict("duration", {"type": "anything"}), None
        )


class TaskScoreView(BaseLoginRequiredTestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        UserProfileFactory(user=self.user)
        self.tasks = TaskFactory.create_batch(10, created_by=self.user)
        self.client.force_login(self.user)
        self.url = reverse("task:score")

    def test_get(self):
        self.assertEqual(self.user.tasks.count(), 10)
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, "task/task-score.html")
        qs = (
            self.user.tasks.filter(
                is_completed=True, duration=Task.TASK_DUERATION_DAILY
            )
            .values("created_at__date")
            .annotate(score=Sum("score"))
            .values("created_at__date", "score")
            .order_by("created_at__date")
        )
        self.assertEqual(list(res.context["tasks_score"].object_list), list(qs))


class TestTaskListView(BaseLoginRequiredTestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        UserProfileFactory(user=self.user)
        self.tasks = TaskFactory.create_batch(10, created_by=self.user)
        self.client.force_login(self.user)
        self.url = reverse("task:list")

    def test_get(self):
        self.assertEqual(self.user.tasks.count(), 10)
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, "task/task-list.html")
        qs = (
            self.user.tasks.filter(duration=Task.TASK_DUERATION_LONG_SHORT_TERM)
            .order_by("-id")
            .values("id", "name", "deadline", "type", "is_completed")
        )
        self.assertEqual(res.context["tasks"].object_list, list(qs))


class TestTaskDailyView(BaseLoginRequiredTestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        UserProfileFactory(user=self.user)
        self.tasks = TaskFactory.create_batch(10, created_by=self.user)
        self.client.force_login(self.user)
        self.url = reverse("task:daily")

    def test_get(self):
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, "task/task-daily.html")
        tasks = (
            self.user.tasks.filter(
                duration=Task.TASK_DUERATION_DAILY,
                created_at__date=timezone.now().date(),
            )
            .distinct()
            .order_by("-id")
        )  # noqa
        score = tasks.values("is_completed").annotate(all_score=Sum("score"))
        earned_score_qs = score.filter(is_completed=True)
        total_score = earned_score = 0
        if earned_score_qs.exists():
            earned_score = earned_score_qs.last()["all_score"]
        if score.exists():
            total_score = score.aggregate(total_score=Sum("all_score"))["total_score"]
        context = res.context
        self.assertEqual(context["total_score"], total_score)
        self.assertEqual(context["earned_score"], earned_score)
        self.assertEqual(
            list(context["tasks"]),
            list(
                tasks.order_by("deadline").values(
                    "id", "name", "deadline", "is_completed", "type"
                )
            ),
        )  # noqa
        self.assertEqual(context["created_at"].date(), timezone.now().date())


class TestTaskDetailView(BaseLoginRequiredTestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        UserProfileFactory(user=self.user)
        self.task = TaskFactory(created_by=self.user)
        self.client.force_login(self.user)
        self.url = reverse("task:detail", kwargs={"pk": self.task.id})

    def test_get(self):
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, "task/task-detail.html")
        self.assertEqual(res.context["task"], self.task)

    def test_get_with_invalid_task(self):
        res = self.client.get(reverse("task:detail", kwargs={"pk": 100}))
        self.assertEqual(res.status_code, 404)

    def test_post(self):
        is_completed = self.task.is_completed
        res = self.client.post(self.url, {"is_completed": True})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(
            res.json(),
            {"message": "Successfully Marked!", "is_completed": not is_completed},
        )
        self.task.refresh_from_db()
        self.assertEqual(self.task.is_completed, not is_completed)


class TestTaskUpdateView(BaseLoginRequiredTestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        UserProfileFactory(user=self.user)
        self.task = TaskFactory(created_by=self.user)
        self.client.force_login(self.user)
        self.url = reverse("task:update", kwargs={"pk": self.task.id})

    def test_get(self):
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, "task/create-task.html")
        self.assertEqual(res.context["form"].instance, self.task)
        self.assertEqual(res.context["form"].__class__, TaskForm)

    def test_post(self):
        data = {
            "name": "New Name",
            "description": "New Description",
            "deadline": timezone.now().date(),
            "type": Task.TASK_TYPE_CRITICAL,
            "duration": Task.TASK_DUERATION_LONG_SHORT_TERM,
        }
        res = self.client.post(self.url, data)
        self.assertEqual(res.status_code, 302)
        self.task.refresh_from_db()
        self.assertEqual(res.url, reverse(get_redirect_url(self.task.duration)))
        self.assertEqual(self.task.name, "New Name")
        self.assertEqual(self.task.description, "New Description")
        self.assertEqual(self.task.deadline.date(), timezone.now().date())
        self.assertEqual(self.task.type, Task.TASK_TYPE_CRITICAL)
        self.assertEqual(self.task.duration, Task.TASK_DUERATION_LONG_SHORT_TERM)


class TestTaskDeleteAPIView(BaseLoginRequiredTestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        UserProfileFactory(user=self.user)
        self.task = TaskFactory(created_by=self.user)
        self.client.force_login(self.user)
        self.url = reverse("task:delete-api", kwargs={"pk": self.task.id})

    def test_post(self):
        res = self.client.post(self.url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), {"success": True})
        self.assertFalse(Task.objects.filter(id=self.task.id).exists())

    def test_delete_with_invalid_task(self):
        res = self.client.post(reverse("task:delete-api", kwargs={"pk": 100}))
        self.assertEqual(res.status_code, 404)


class TestTaskDeleteView(BaseLoginRequiredTestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        UserProfileFactory(user=self.user)
        self.task = TaskFactory(created_by=self.user)
        self.client.force_login(self.user)
        self.url = reverse("task:delete", kwargs={"pk": self.task.id})

    def test_post(self):
        duration = self.task.duration
        res = self.client.post(self.url)
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res.url, reverse(get_redirect_url(duration)))
        self.assertFalse(Task.objects.filter(id=self.task.id).exists())

    def test_delete_with_invalid_task(self):
        res = self.client.post(reverse("task:delete", kwargs={"pk": 100}))
        self.assertEqual(res.status_code, 404)
