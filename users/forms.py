from django import forms
from django.contrib.auth import authenticate

from users.models import User


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
            raise forms.ValidationError("Неверный email или пароль")

        data["user"] = user
        return data
