from django.contrib.auth import get_user_model

from projects.models import Project
from skills.models import Skill
from team_finder.constants import PROJECT_STATUS_CLOSED

User = get_user_model()


def get_project_list_queryset(skill=None):
    queryset = (
        Project.objects
        .select_related("owner")
        .prefetch_related("participants", "skills")
    )

    if skill is not None:
        queryset = queryset.filter(skills=skill).distinct()

    return queryset


def get_project_detail_queryset():
    return (
        Project.objects
        .select_related("owner")
        .prefetch_related("participants", "skills")
    )


def create_project(form, user: User) -> Project:
    project = form.save(commit=False)
    project.owner = user
    project.save()
    project.participants.add(user)
    return project


def toggle_participation(project: Project, user: User) -> bool:
    if project.status == PROJECT_STATUS_CLOSED:
        raise ValueError("Project is closed")

    is_participant = project.participants.filter(pk=user.pk).exists()

    if is_participant:
        project.participants.remove(user)
        return False

    project.participants.add(user)
    return True


def complete_project(project: Project):
    project.status = PROJECT_STATUS_CLOSED
    project.save(update_fields=["status"])


def add_skill_to_project(
    project: Project, skill: Skill
) -> tuple[int, bool, bool]:
    created = False

    if project.skills.filter(pk=skill.pk).exists():
        return skill.pk, created, False

    project.skills.add(skill)
    return skill.pk, created, True


def remove_skill_from_project(project: Project, skill: Skill) -> bool:
    if not project.skills.filter(pk=skill.pk).exists():
        return False

    project.skills.remove(skill)
    return True
