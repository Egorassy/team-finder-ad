from django.urls import path

from projects.views import (
    add_project_skill_view,
    complete_project_view,
    create_project_view,
    edit_project_view,
    project_detail_view,
    project_list_view,
    project_skill_autocomplete,
    remove_project_skill_view,
    toggle_participate_view,
)

urlpatterns = [
    path("list/", project_list_view),
    path("create-project/", create_project_view),
    path("<int:pk>/edit/", edit_project_view),
    path("<int:pk>/", project_detail_view),

    path("<int:pk>/toggle-participate/", toggle_participate_view),
    path("<int:pk>/complete/", complete_project_view),

    path("skills/", project_skill_autocomplete),

    path("<int:pk>/skills/add/", add_project_skill_view),
    path("<int:pk>/skills/<int:skill_id>/remove/", remove_project_skill_view),
]
