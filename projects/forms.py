from django import forms

from projects.models import Project
from projects.utils import is_valid_github_url


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ("name", "description", "github_url", "status")
        labels = {
            "name": "Название проекта",
            "description": "Описание проекта",
            "github_url": "Ссылка на GitHub",
            "status": "Статус проекта",
        }

    def clean_github_url(self):
        url = self.cleaned_data.get("github_url")

        if not is_valid_github_url(url):
            raise forms.ValidationError("Invalid GitHub URL")

        return url
