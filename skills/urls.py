from django.urls import path

from skills.views import skill_autocomplete_view

app_name = "skills"

urlpatterns = [
    path("", skill_autocomplete_view, name="autocomplete"),
]
