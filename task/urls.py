from django.urls import path
from . import views


app_name = "task"

urlpatterns = [
    path("score/", views.TaskScoreView.as_view(), name="score"),
    path("create/", views.TaskCreateView.as_view(), name="create"),
    path("list/", views.TaskListView.as_view(), name="list"),
    path("daily/", views.TaskDailyView.as_view(), name="daily"),
    path("<int:pk>/", views.TaskDetailView.as_view(), name="detail"),
    path("<int:pk>/update/", views.TaskUpdateView.as_view(), name="update"),
    path("api/<int:pk>/delete/", views.TaskDeleteAPIView.as_view(), name="delete-api"),
    path("<int:pk>/delete/", views.TaskDeleteView.as_view(), name="delete"),
]
