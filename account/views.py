from django.contrib.auth import logout
from django.views import View
from django.shortcuts import render, redirect
from .forms import SignUpForm, LoginFrom
from django.urls import reverse


class SignUpView(View):
    def get(self, request):
        form = SignUpForm(request=request)
        return render(request, "account/signup.html", {"form": form})

    def post(self, request):
        form = SignUpForm(request.POST, request=request)
        if form.is_valid():
            form.save()
            form.login()
            return redirect("task:list")
        return render(request, "account/signup.html", {"form": form})


class LoginView(View):
    def get(self, request):
        form = LoginFrom(request=request)
        return render(request, "account/login.html", {"form": form})

    def post(self, request):
        success_url = request.GET.get("next") or reverse("task:list")

        form = LoginFrom(request.POST, request=request)
        if form.is_valid():
            form.login()
            return redirect(success_url)
        return render(request, "account/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("account:login")
