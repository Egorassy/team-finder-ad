from skills.models import Skill
from skills.utils import normalize_skill_query
from team_finder.constants import SKILL_AUTOCOMPLETE_LIMIT


def search_skills(query: str):
    query = normalize_skill_query(query)

    if not query:
        return Skill.objects.none()

    return (
        Skill.objects
        .filter(name__istartswith=query)
        .order_by("name")[:SKILL_AUTOCOMPLETE_LIMIT]
    )
