import json
from http import HTTPStatus

from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET, require_POST

from projects.forms import ProjectForm
from projects.models import Project
from projects.services import (
    add_skill_to_project,
    complete_project,
    create_project,
    get_project_detail_queryset,
    get_project_list_queryset,
    remove_skill_from_project,
    toggle_participation,
)
from projects.utils import build_query_prefix, paginate_queryset
from skills.models import Skill
from skills.services import search_skills
from team_finder.constants import (
    PROJECT_ALREADY_CLOSED_MESSAGE,
    PROJECT_CLOSED_MESSAGE,
    PROJECT_NOT_FOUND_MESSAGE,
    PROJECT_STATUS_CLOSED,
    PROJECT_STATUS_OPEN,
    AUTHENTICATION_REQUIRED_MESSAGE,
    FORBIDDEN_MESSAGE,
    SKILL_DATA_REQUIRED_MESSAGE,
    SKILL_NOT_ATTACHED_MESSAGE,
    SKILL_NOT_FOUND_MESSAGE,
)


def _json_error(message: str, status_code: HTTPStatus):
    return JsonResponse(
        {"status": "error", "message": message},
        status=status_code,
    )


def _not_found(message: str):
    return _json_error(message, HTTPStatus.NOT_FOUND)


def project_list_view(request):
    skill_name = request.GET.get("skill", "").strip()
    active_skill = None

    projects_queryset = get_project_list_queryset()

    if skill_name:
        active_skill = Skill.objects.filter(name=skill_name).first()
        if active_skill is None:
            return _not_found(SKILL_NOT_FOUND_MESSAGE)

        projects_queryset = get_project_list_queryset(skill=active_skill)

    page_obj = paginate_queryset(request, projects_queryset)
    all_skills = Skill.objects.order_by("name")
    query_prefix = (
        build_query_prefix({"skill": active_skill.name})
        if active_skill
        else ""
    )

    return render(
        request,
        "projects/project_list.html",
        {
            "projects": page_obj.object_list,
            "page_obj": page_obj,
            "all_skills": all_skills,
            "active_skill": active_skill,
            "query_prefix": query_prefix,
        },
    )


def project_detail_view(request, pk):
    project = get_project_detail_queryset().filter(pk=pk).first()

    if project is None:
        return _not_found(PROJECT_NOT_FOUND_MESSAGE)

    return render(
        request,
        "projects/project-details.html",
        {"project": project},
    )


def create_project_view(request):
    if not request.user.is_authenticated:
        return redirect("users:login")

    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = create_project(form, request.user)
            return redirect("projects:detail", pk=project.pk)
    else:
        form = ProjectForm()

    return render(
        request,
        "projects/create-project.html",
        {
            "form": form,
            "is_edit": False,
        },
    )


def edit_project_view(request, pk):
    if not request.user.is_authenticated:
        return redirect("users:login")

    project = Project.objects.filter(pk=pk, owner=request.user).first()
    if project is None:
        return _not_found(PROJECT_NOT_FOUND_MESSAGE)

    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect("projects:detail", pk=project.pk)
    else:
        form = ProjectForm(instance=project)

    return render(
        request,
        "projects/create-project.html",
        {
            "form": form,
            "is_edit": True,
        },
    )


@require_POST
def toggle_participate_view(request, pk):
    if not request.user.is_authenticated:
        return _json_error(
            AUTHENTICATION_REQUIRED_MESSAGE,
            HTTPStatus.UNAUTHORIZED,
        )

    project = Project.objects.filter(pk=pk).first()
    if project is None:
        return _not_found(PROJECT_NOT_FOUND_MESSAGE)

    if project.status == PROJECT_STATUS_CLOSED:
        return _json_error(
            PROJECT_CLOSED_MESSAGE,
            HTTPStatus.BAD_REQUEST,
        )

    participant = toggle_participation(project, request.user)

    return JsonResponse(
        {
            "status": "ok",
            "participant": participant,
        }
    )


@require_POST
def complete_project_view(request, pk):
    if not request.user.is_authenticated:
        return _json_error(
            AUTHENTICATION_REQUIRED_MESSAGE,
            HTTPStatus.UNAUTHORIZED,
        )

    project = Project.objects.filter(pk=pk).first()
    if project is None:
        return _not_found(PROJECT_NOT_FOUND_MESSAGE)

    if project.owner != request.user:
        return _json_error(FORBIDDEN_MESSAGE, HTTPStatus.FORBIDDEN)

    if project.status != PROJECT_STATUS_OPEN:
        return _json_error(
            PROJECT_ALREADY_CLOSED_MESSAGE,
            HTTPStatus.BAD_REQUEST,
        )

    complete_project(project)

    return JsonResponse(
        {
            "status": "ok",
            "project_status": PROJECT_STATUS_CLOSED,
        }
    )


@require_GET
def project_skill_autocomplete(request):
    query = request.GET.get("q", "")
    skills = search_skills(query)

    return JsonResponse(
        list(skills.values("id", "name")),
        safe=False,
    )


@require_POST
def add_project_skill_view(request, pk):
    if not request.user.is_authenticated:
        return _json_error(
            AUTHENTICATION_REQUIRED_MESSAGE,
            HTTPStatus.UNAUTHORIZED,
        )

    project = Project.objects.filter(pk=pk).first()
    if project is None:
        return _not_found(PROJECT_NOT_FOUND_MESSAGE)

    if project.owner != request.user:
        return _json_error(FORBIDDEN_MESSAGE, HTTPStatus.FORBIDDEN)

    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        payload = {}

    skill_id = payload.get("skill_id")
    name = (payload.get("name") or "").strip()

    if skill_id:
        skill = Skill.objects.filter(pk=skill_id).first()
        if skill is None:
            return _not_found(SKILL_NOT_FOUND_MESSAGE)
        skill_pk, created, added = add_skill_to_project(project, skill)
    elif name:
        skill, created = Skill.objects.get_or_create(name=name)
        skill_pk, _, added = add_skill_to_project(project, skill)
    else:
        return _json_error(SKILL_DATA_REQUIRED_MESSAGE, HTTPStatus.BAD_REQUEST)

    skill = Skill.objects.filter(pk=skill_pk).first()
    if skill is None:
        return _not_found(SKILL_NOT_FOUND_MESSAGE)

    return JsonResponse(
        {
            "id": skill.pk,
            "name": skill.name,
            "skill_id": skill.pk,
            "created": created,
            "added": added,
        }
    )


@require_POST
def remove_project_skill_view(request, pk, skill_id):
    if not request.user.is_authenticated:
        return _json_error(
            AUTHENTICATION_REQUIRED_MESSAGE,
            HTTPStatus.UNAUTHORIZED,
        )

    project = Project.objects.filter(pk=pk).first()
    if project is None:
        return _not_found(PROJECT_NOT_FOUND_MESSAGE)

    skill = Skill.objects.filter(pk=skill_id).first()
    if skill is None:
        return _not_found(SKILL_NOT_FOUND_MESSAGE)

    if project.owner != request.user:
        return _json_error(FORBIDDEN_MESSAGE, HTTPStatus.FORBIDDEN)

    removed = remove_skill_from_project(project, skill)

    if not removed:
        return _json_error(
            SKILL_NOT_ATTACHED_MESSAGE,
            HTTPStatus.BAD_REQUEST,
        )

    return JsonResponse(
        {
            "status": "ok",
            "removed": True,
        }
    )
