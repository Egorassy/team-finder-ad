from django.shortcuts import render, redirect
from django.contrib.auth import login

from users.forms import RegisterForm, LoginForm
from users.services import create_user_from_form


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = create_user_from_form(form)
            login(request, user)
            return redirect("/projects/list/")
    else:
        form = RegisterForm()

    return render(request, "users/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            login(request, form.cleaned_data["user"])
            return redirect("/projects/list/")
    else:
        form = LoginForm()

    return render(request, "users/login.html", {"form": form})
