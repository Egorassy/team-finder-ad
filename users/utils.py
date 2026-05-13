import re
import secrets

from django.core.paginator import Paginator

from team_finder.constants import (
    GITHUB_URL_REGEX,
    PAGINATION_PAGE_SIZE,
    PHONE_COUNTRY_CODE_PREFIX,
    PHONE_DIGITS_COUNT,
    PHONE_NATIONAL_PREFIX,
    PHONE_REGEX,
)


def normalize_phone(phone: str) -> str:
    phone = phone.strip()

    if phone.startswith(PHONE_NATIONAL_PREFIX):
        return f"{PHONE_COUNTRY_CODE_PREFIX}{phone[1:]}"

    return phone


def is_valid_phone(phone: str) -> bool:
    return bool(re.match(PHONE_REGEX, phone))


def is_github_url(url: str | None) -> bool:
    if not url:
        return True

    return bool(re.match(GITHUB_URL_REGEX, url))


def generate_placeholder_phone() -> str:
    from users.models import User

    while True:
        digits_part = "".join(
            str(secrets.randbelow(10))
            for _ in range(PHONE_DIGITS_COUNT)
        )
        phone = f"{PHONE_COUNTRY_CODE_PREFIX}{digits_part}"

        if not User.objects.filter(phone=phone).exists():
            return phone


def paginate_queryset(request, queryset, page_size: int = PAGINATION_PAGE_SIZE):
    paginator = Paginator(queryset, page_size)
    return paginator.get_page(request.GET.get("page"))
