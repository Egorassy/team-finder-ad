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


def update_user_profile(form):
    return form.save()
