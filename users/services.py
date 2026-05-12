from users.models import User


def create_user_from_form(form):
    user = User(
        email=form.cleaned_data["email"],
        name=form.cleaned_data["name"],
        surname=form.cleaned_data["surname"],
    )
    user.set_password(form.cleaned_data["password"])
    user.save()
    return user
