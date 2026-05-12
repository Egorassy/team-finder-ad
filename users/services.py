from users.models import User
from users.utils import normalize_phone


def create_user_from_form(form):
    user = User(
        email=form.cleaned_data["email"],
        name=form.cleaned_data["name"],
        surname=form.cleaned_data["surname"],
    )
    user.set_password(form.cleaned_data["password"])
    user.save()
    return user


def update_user_profile(user: User, form):
    user.name = form.cleaned_data["name"]
    user.surname = form.cleaned_data["surname"]
    user.about = form.cleaned_data.get("about", "")
    user.github_url = form.cleaned_data.get("github_url")

    phone = form.cleaned_data.get("phone")
    if phone:
        user.phone = normalize_phone(phone)

    avatar = form.cleaned_data.get("avatar")
    if avatar:
        user.avatar = avatar

    user.save()
    return user
