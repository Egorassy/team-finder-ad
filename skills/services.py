from skills.models import Skill
from skills.utils import normalize_skill_query


def search_skills(query: str):
    query = normalize_skill_query(query)

    if not query:
        return Skill.objects.none()

    return (
        Skill.objects
        .filter(name__istartswith=query)
        .order_by("name")[:10]
    )
