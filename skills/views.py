from django.http import JsonResponse
from django.views.decorators.http import require_GET

from skills.services import search_skills


@require_GET
def skill_autocomplete_view(request):
    query = request.GET.get("q", "")
    skills = search_skills(query)

    data = list(skills.values("id", "name"))

    return JsonResponse(data, safe=False)
