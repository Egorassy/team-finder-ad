from django.http import JsonResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from projects.models import Project
from projects.forms import ProjectForm
from projects.services import (
    create_project,
    toggle_participation,
    complete_project,
    add_skill_to_project,
    remove_skill_from_project,
)
from skills.models import Skill
from skills.services import search_skills


def project_list_view(request):
    projects = Project.objects.all()
    return render(request, "projects/project_list.html", {"projects": projects})


def project_detail_view(request, pk):
    project = get_object_or_404(Project, pk=pk)
    return render(request, "projects/project-details.html", {"project": project})


@login_required
def toggle_participate_view(request, pk):
    project = get_object_or_404(Project, pk=pk)
    status = toggle_participation(project, request.user)
    return JsonResponse({"status": "ok", "participating": status})


@login_required
def complete_project_view(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if project.owner != request.user or project.status != "open":
        return JsonResponse({"status": "error"}, status=403)

    complete_project(project)
    return JsonResponse({"status": "ok", "project_status": "closed"})


@require_GET
def project_skill_autocomplete(request):
    q = request.GET.get("q", "")
    skills = search_skills(q)
    return JsonResponse(list(skills.values("id", "name")), safe=False)


@login_required
def add_project_skill_view(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if project.owner != request.user:
        return JsonResponse({"status": "error"}, status=403)

    skill_id = request.POST.get("skill_id")
    name = request.POST.get("name")

    if skill_id:
        skill = get_object_or_404(Skill, id=skill_id)
        sid, created, added = add_skill_to_project(project, skill)
    else:
        skill, created = Skill.objects.get_or_create(name=name)
        sid, _, added = add_skill_to_project(project, skill)

    return JsonResponse(
        {
            "skill_id": sid,
            "created": created,
            "added": added,
        }
    )


@login_required
def remove_project_skill_view(request, pk, skill_id):
    project = get_object_or_404(Project, pk=pk)
    skill = get_object_or_404(Skill, id=skill_id)

    if project.owner != request.user:
        return JsonResponse({"status": "error"}, status=403)

    removed = remove_skill_from_project(project, skill)

    return JsonResponse({"status": "ok", "removed": removed})
