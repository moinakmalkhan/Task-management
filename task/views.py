from django.core.paginator import Paginator
from django.http import Http404
from django.utils import timezone
from django.shortcuts import render, redirect
from django.views import View
from django.db.models import Sum
from task.forms import TaskForm
from task.models import Task
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist

TASK_MODEL_FIELDS_NAME = [field.name for field in Task._meta.fields]


def get_redirect_url(duration):
    """
    Get redirect url from task.
    """
    return "task:daily" if duration == Task.TASK_DUERATION_DAILY else "task:list"


def get_data_to_search(data, exclude_fields=[]):
    return {
        d: data[d]
        for d in data
        if d.split("__")[0] in TASK_MODEL_FIELDS_NAME
        and d.split("__")[0] not in exclude_fields
    }  # noqa


def check_field_in_search_dict(field, search_dict):
    return any([field in f for f in search_dict])


def get_field_in_search_dict(field, search_dict):
    for f in search_dict:
        if field in f:
            return search_dict[f]


class TaskCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = TaskForm(request=request)
        return render(request, "task/create-task.html", {"form": form})

    def post(self, request):
        form = TaskForm(request.POST, request=request)
        if form.is_valid():
            form.save()
            return redirect(get_redirect_url(form.instance.duration))
        return render(request, "task/create-task.html", {"form": form})


class TaskScoreView(LoginRequiredMixin, View):
    template_name = "task/task-score.html"

    def get(self, request):
        data = request.GET.dict()
        from_ = data.pop("from", None)
        to = data.pop("to", None)
        data_to_search = get_data_to_search(data, ["duration"])
        tasks = request.user.tasks.filter(
            **data_to_search, duration=Task.TASK_DUERATION_DAILY
        ).distinct()
        if from_ and to:
            tasks = tasks.filter(created_at__date__gte=from_, created_at__date__lte=to)
        tasks_score = (
            tasks.filter(is_completed=True)
            .values("created_at__date")
            .annotate(score=Sum("score"))
            .values("created_at__date", "score")
            .order_by("created_at__date")
        )
        paginator = Paginator(tasks_score, 50)
        page = data.get("page", 1)
        tasks_score = paginator.get_page(page)
        context = {
            "tasks_score": tasks_score,
            "task_types": Task.TASK_TYPES,
        }
        return render(request, self.template_name, context)


class TaskListView(LoginRequiredMixin, View):
    template_name = "task/task-list.html"

    def get(self, request):
        data = request.GET.dict()
        data_to_search = get_data_to_search(data, ["duration"])
        tasks = request.user.tasks.filter(
            **data_to_search, duration=Task.TASK_DUERATION_LONG_SHORT_TERM
        ).distinct()  # noqa
        tasks = tasks.order_by("-id").values(
            "id", "name", "deadline", "type", "is_completed"
        )
        paginator = Paginator(tasks, 10)
        page = data.get("page", 1)
        tasks = paginator.get_page(page)
        context = {
            "tasks": tasks,
            "task_types": Task.TASK_TYPES,
        }
        return render(request, self.template_name, context)


class TaskDailyView(LoginRequiredMixin, View):
    template_name = "task/task-daily.html"

    def get(self, request):
        data = request.GET.dict()
        data_to_search = get_data_to_search(data, ["duration"])
        if not check_field_in_search_dict("created_at", data_to_search):
            data_to_search["created_at__date"] = timezone.now().date()
        tasks = (
            request.user.tasks.filter(
                **data_to_search, duration=Task.TASK_DUERATION_DAILY
            )
            .distinct()
            .order_by("-id")
        )  # noqa
        score = tasks.values("is_completed").annotate(all_score=Sum("score"))
        earned_score = total_score = 0
        if score.exists():
            earned_score_qs = score.filter(is_completed=True)
            if earned_score_qs.exists():
                earned_score = earned_score_qs.last()["all_score"]
            total_score = score.aggregate(total_score=Sum("all_score"))["total_score"]

        context = {
            "tasks": tasks.order_by("deadline").values(
                "id", "name", "deadline", "is_completed", "type"
            ),
            "total_score": total_score,
            "earned_score": earned_score,
            "created_at": timezone.datetime.strptime(
                str(get_field_in_search_dict("created_at", data_to_search)), "%Y-%m-%d"
            ),  # noqa
        }
        return render(request, self.template_name, context)


class TaskDetailView(LoginRequiredMixin, View):
    template_name = "task/task-detail.html"

    def get(self, request, pk):
        try:
            task = request.user.tasks.get(pk=pk)
        except ObjectDoesNotExist:
            raise Http404
        return render(request, self.template_name, {"task": task})

    def post(self, request, pk):
        try:
            task = request.user.tasks.get(pk=pk)
        except ObjectDoesNotExist:
            raise Http404
        task.is_completed = not task.is_completed
        task.save(update_fields=["is_completed"])
        return JsonResponse(
            {"message": "Successfully Marked!", "is_completed": task.is_completed},
            status=200,
        )


class TaskUpdateView(LoginRequiredMixin, View):
    template_name = "task/create-task.html"

    def get(self, request, pk):
        try:
            task = request.user.tasks.get(pk=pk)
        except ObjectDoesNotExist:
            raise Http404
        form = TaskForm(instance=task, request=request)
        return render(request, self.template_name, {"form": form})

    def post(self, request, pk):
        try:
            task = request.user.tasks.get(pk=pk)
        except ObjectDoesNotExist:
            raise Http404
        form = TaskForm(request.POST, instance=task, request=request)
        if form.is_valid():
            form.save()
            return redirect(get_redirect_url(task.duration))
        return render(request, self.template_name, {"form": form})


class TaskDeleteAPIView(LoginRequiredMixin, View):
    def post(self, request, pk):
        try:
            task = request.user.tasks.get(pk=pk)
        except ObjectDoesNotExist:
            raise Http404
        task.delete()
        return JsonResponse({"success": True})


class TaskDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        try:
            task = request.user.tasks.get(pk=pk)
        except ObjectDoesNotExist:
            raise Http404
        duration = task.duration
        task.delete()
        return redirect(get_redirect_url(duration))
