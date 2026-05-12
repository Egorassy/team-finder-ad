from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

from team_finder.views import root_redirect

urlpatterns = [
    path("", root_redirect),
    path("admin/", admin.site.urls),
    path("users/", include("users.urls")),
    path("projects/", include("projects.urls")),
    path("skills/", include("skills.urls")),
]
