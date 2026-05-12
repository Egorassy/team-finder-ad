import re

from team_finder.constants import (
    GITHUB_URL_REGEX,
    PHONE_REGEX,
)


def normalize_phone(phone: str) -> str:
    phone = phone.strip()

    if phone.startswith("8"):
        return "+7" + phone[1:]

    return phone


def is_valid_phone(phone: str) -> bool:
    return bool(
        re.match(PHONE_REGEX, phone)
    )


def is_github_url(url: str | None) -> bool:
    if not url:
        return True

    return bool(
        re.match(GITHUB_URL_REGEX, url)
    )
