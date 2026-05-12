from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from users.managers import UserManager
from team_finder.constants import (
    USER_NAME_MAX_LENGTH,
    USER_SURNAME_MAX_LENGTH,
    USER_PHONE_MAX_LENGTH,
    USER_ABOUT_MAX_LENGTH,
)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)

    name = models.CharField(max_length=USER_NAME_MAX_LENGTH)
    surname = models.CharField(max_length=USER_SURNAME_MAX_LENGTH)

    avatar = models.ImageField(upload_to="avatars/")

    phone = models.CharField(max_length=USER_PHONE_MAX_LENGTH, unique=True)

    github_url = models.URLField(blank=True, null=True)
    about = models.CharField(max_length=USER_ABOUT_MAX_LENGTH, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname"]

    def __str__(self):
        return self.email
