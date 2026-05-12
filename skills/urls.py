from django.urls import path
from skills.views import skill_autocomplete_view


urlpatterns = [
    path("", skill_autocomplete_view),
]
