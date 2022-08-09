from django.db import models
from django.contrib.auth import get_user_model


class Task(models.Model):
    TASK_TYPE_MOST_IMPORTANT = "Most Important"
    TASK_TYPE_CRITICAL = "Critical"
    TASK_TYPE_OTHER = "Other"
    TASK_TYPES = (TASK_TYPE_MOST_IMPORTANT, TASK_TYPE_CRITICAL, TASK_TYPE_OTHER)
    TASK_DUERATION_DAILY = "Daily"
    TASK_DUERATION_LONG_SHORT_TERM = "Long-Short term"
    TASK_DUERATIONS = (TASK_DUERATION_DAILY, TASK_DUERATION_LONG_SHORT_TERM)
    is_completed = models.BooleanField(default=False)
    name = models.CharField(max_length=200)
    description = models.TextField()
    deadline = models.DateTimeField()
    created_by = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="tasks"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    score = models.IntegerField(default=1)
    type = models.CharField(
        max_length=20,
        choices=((i, i) for i in TASK_TYPES),
        default=TASK_TYPE_MOST_IMPORTANT,
    )
    duration = models.CharField(
        max_length=20,
        choices=((i, i) for i in TASK_DUERATIONS),
        default=TASK_DUERATION_LONG_SHORT_TERM,
    )

    def __str__(self):
        return self.name
