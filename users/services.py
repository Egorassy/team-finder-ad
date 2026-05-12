from users.models import User


def create_user_from_form(form):
    return User.objects.create_user(
        email=form.cleaned_data["email"],
        password=form.cleaned_data["password"],
        name=form.cleaned_data["name"],
        surname=form.cleaned_data["surname"],
    )


def update_user_profile(form):
    return form.save()
