from django.contrib.auth import get_user_model

from projects.models import Project
from skills.models import Skill

User = get_user_model()


def create_project(form, user: User) -> Project:
    project = form.save(commit=False)
    project.owner = user
    project.save()

    project.participants.add(user)

    return project


def toggle_participation(project: Project, user: User) -> bool:
    if user in project.participants.all():
        project.participants.remove(user)
        return False

    project.participants.add(user)
    return True


def complete_project(project: Project):
    project.status = "closed"
    project.save(update_fields=["status"])


def add_skill_to_project(project: Project, skill: Skill) -> tuple[bool, bool]:
    created = False

    if project.skills.filter(id=skill.id).exists():
        return skill.id, created, False

    project.skills.add(skill)
    return skill.id, created, True


def remove_skill_from_project(project: Project, skill: Skill) -> bool:
    if not project.skills.filter(id=skill.id).exists():
        return False

    project.skills.remove(skill)
    return True
