import re

from django import forms
from django.contrib.auth import authenticate

from team_finder.constants import GITHUB_URL_REGEX
from users.models import User
from users.utils import (
    is_github_url,
    is_valid_phone,
    normalize_phone,
)


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ("name", "surname", "email", "password")


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        data = super().clean()

        user = authenticate(
            email=data.get("email"),
            password=data.get("password"),
        )

        if not user:
            raise forms.ValidationError(
                "Неверный email или пароль"
            )

        data["user"] = user

        return data


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            "name",
            "surname",
            "avatar",
            "about",
            "phone",
            "github_url",
        )

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")

        normalized_phone = normalize_phone(phone)

        if not is_valid_phone(normalized_phone):
            raise forms.ValidationError(
                "Invalid phone format"
            )

        existing_user = (
            User.objects
            .exclude(pk=self.instance.pk)
            .filter(phone=normalized_phone)
            .exists()
        )

        if existing_user:
            raise forms.ValidationError(
                "Phone already exists"
            )

        return normalized_phone

    def clean_github_url(self):
        url = self.cleaned_data.get("github_url")

        if not is_github_url(url):
            raise forms.ValidationError(
                "Invalid GitHub URL"
            )

        return url
