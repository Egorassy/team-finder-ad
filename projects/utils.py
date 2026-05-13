import re
from urllib.parse import urlencode

from django.core.paginator import Paginator

from team_finder.constants import GITHUB_URL_REGEX, PAGINATION_PAGE_SIZE


def is_valid_github_url(url: str) -> bool:
    if not url:
        return True
    return bool(re.match(GITHUB_URL_REGEX, url))


def paginate_queryset(
    request,
    queryset,
    page_size: int = PAGINATION_PAGE_SIZE,
):
    paginator = Paginator(queryset, page_size)
    return paginator.get_page(request.GET.get("page"))


def build_query_prefix(params: dict[str, str] | None = None) -> str:
    if not params:
        return ""
    return f"{urlencode(params)}&"
