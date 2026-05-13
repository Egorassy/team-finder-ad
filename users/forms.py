from django import forms
from django.contrib.auth.forms import (
    PasswordChangeForm,
    ReadOnlyPasswordHashField,
)

from users.models import User
from users.utils import (
    generate_placeholder_phone,
    is_github_url,
    is_valid_phone,
    normalize_phone,
)
from team_finder.constants import (
    INVALID_PHONE_MESSAGE,
    PHONE_REQUIRED_MESSAGE,
    PHONE_EXISTS_MESSAGE,
    INVALID_GITHUB_URL_MESSAGE,
    PASSWORDS_DONT_MATCH_MESSAGE,
    INVALID_LOGIN_CREDENTIALS_MESSAGE,
)


class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput,
    )

    class Meta:
        model = User
        fields = ("name", "surname", "email", "password")
        labels = {
            "name": "Имя",
            "surname": "Фамилия",
            "email": "Email",
            "password": "Пароль",
        }


class LoginForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput,
    )

    def clean(self):
        cleaned_data = super().clean()

        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        user = User.objects.filter(email=email).first()
        if user is None or not user.check_password(password):
            raise forms.ValidationError(INVALID_LOGIN_CREDENTIALS_MESSAGE)

        user.backend = "django.contrib.auth.backends.ModelBackend"
        cleaned_data["user"] = user
        return cleaned_data


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("name", "surname", "avatar", "about", "phone", "github_url")
        labels = {
            "name": "Имя",
            "surname": "Фамилия",
            "avatar": "Аватар",
            "about": "О себе",
            "phone": "Телефон",
            "github_url": "Ссылка на GitHub",
        }
        widgets = {
            "about": forms.Textarea(attrs={"rows": 4}),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")

        if not phone:
            raise forms.ValidationError(PHONE_REQUIRED_MESSAGE)

        normalized_phone = normalize_phone(phone)

        if not is_valid_phone(normalized_phone):
            raise forms.ValidationError(INVALID_PHONE_MESSAGE)

        users_queryset = User.objects.all()
        if self.instance.pk:
            users_queryset = users_queryset.exclude(pk=self.instance.pk)

        if users_queryset.filter(phone=normalized_phone).exists():
            raise forms.ValidationError(PHONE_EXISTS_MESSAGE)

        return normalized_phone

    def clean_github_url(self):
        url = self.cleaned_data.get("github_url")

        if not is_github_url(url):
            raise forms.ValidationError(INVALID_GITHUB_URL_MESSAGE)

        return url


class ChangePasswordForm(PasswordChangeForm):
    pass


class AdminUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput,
    )
    password2 = forms.CharField(
        label="Подтвердите пароль",
        widget=forms.PasswordInput,
    )

    class Meta:
        model = User
        fields = ("email", "name", "surname")
        labels = {
            "email": "Email",
            "name": "Имя",
            "surname": "Фамилия",
        }

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(PASSWORDS_DONT_MATCH_MESSAGE)

        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.phone = generate_placeholder_phone()
        user.set_password(self.cleaned_data["password1"])

        if commit:
            user.save()

        return user


class AdminUserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(label="Пароль")

    class Meta:
        model = User
        fields = (
            "email",
            "name",
            "surname",
            "avatar",
            "phone",
            "github_url",
            "about",
            "password",
            "is_active",
            "is_staff",
            "is_superuser",
            "groups",
            "user_permissions",
        )
        labels = {
            "email": "Email",
            "name": "Имя",
            "surname": "Фамилия",
            "avatar": "Аватар",
            "phone": "Телефон",
            "github_url": "Ссылка на GitHub",
            "about": "О себе",
        }
