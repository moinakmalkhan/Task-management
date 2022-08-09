from django import forms
from .models import Task


class TaskForm(forms.ModelForm):
    deadline = forms.DateTimeField(
        widget=forms.DateTimeInput(
            format="%Y-%m-%dT%H:%M", attrs={"type": "datetime-local"}
        )
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        # add form-control class for bootstrap and add placeholder
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"

    def save(self, commit=True):
        task = super().save(commit=False)
        task.created_by = self.request.user
        duration = self.request.GET.get("duration")
        if duration not in Task.TASK_DUERATIONS:
            duration = Task.TASK_DUERATION_LONG_SHORT_TERM
        task.duration = duration
        if commit:
            task.save()
        return task

    class Meta:
        model = Task
        fields = ["name", "description", "deadline", "type"]
