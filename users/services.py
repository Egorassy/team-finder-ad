from users.models import User


def create_user_from_form(form):
    user = User.objects.create_user(
        email=form.cleaned_data["email"],
        password=form.cleaned_data["password"],
        name=form.cleaned_data["name"],
        surname=form.cleaned_data["surname"],
    )
    user.backend = "django.contrib.auth.backends.ModelBackend"
    return user


def update_user_profile(user, form):
    user.name = form.cleaned_data["name"]
    user.surname = form.cleaned_data["surname"]
    user.about = form.cleaned_data.get("about", "")
    user.github_url = form.cleaned_data.get("github_url")

    phone = form.cleaned_data.get("phone")
    if phone:
        user.phone = phone

    avatar = form.cleaned_data.get("avatar")
    if avatar:
        user.avatar = avatar

    user.save()
    return user
