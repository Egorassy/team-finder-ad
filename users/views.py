from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from users.forms import (
    ChangePasswordForm,
    LoginForm,
    RegisterForm,
    UserProfileForm,
)
from users.models import User
from users.services import create_user_from_form, update_user_profile
from users.utils import paginate_queryset


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = create_user_from_form(form)
            login(request, user)
            return redirect("/projects/list/")
    else:
        form = RegisterForm()

    return render(
        request,
        "includes/users/register.html",
        {"form": form},
    )


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            login(request, form.cleaned_data["user"])
            return redirect("/projects/list/")
    else:
        form = LoginForm()

    return render(
        request,
        "users/login.html",
        {"form": form},
    )


def logout_view(request):
    logout(request)
    return redirect("/projects/list/")


def user_detail_view(request, pk):
    user = get_object_or_404(
        User.objects.prefetch_related(
            "owned_projects__participants",
            "owned_projects__skills",
        ),
        pk=pk,
    )

    return render(
        request,
        "users/user-details.html",
        {"user": user},
    )


def users_list_view(request):
    participants_queryset = User.objects.order_by("id")
    page_obj = paginate_queryset(request, participants_queryset)

    return render(
        request,
        "users/participants.html",
        {
            "participants": participants_queryset,
            "page_obj": page_obj,
            "query_prefix": "",
        },
    )


@login_required
def edit_profile_view(request):
    if request.method == "POST":
        form = UserProfileForm(
            request.POST,
            request.FILES,
            instance=request.user,
        )
        if form.is_valid():
            update_user_profile(request.user, form)
            return redirect(f"/users/{request.user.id}/")
    else:
        form = UserProfileForm(instance=request.user)

    return render(
        request,
        "users/edit_profile.html",
        {
            "form": form,
            "user": request.user,
        },
    )


@login_required
def change_password_view(request):
    if request.method == "POST":
        form = ChangePasswordForm(
            user=request.user,
            data=request.POST,
        )
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect(f"/users/{request.user.id}/")
    else:
        form = ChangePasswordForm(user=request.user)

    return render(
        request,
        "users/change_password.html",
        {"form": form},
    )
