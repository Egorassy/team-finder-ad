import re


PHONE_PATTERN = re.compile(r"^(8|\+7)\d{10}$")


def normalize_phone(phone: str) -> str:
    phone = phone.strip()
    if phone.startswith("+7"):
        return phone
    if phone.startswith("8"):
        return "+7" + phone[1:]
    return phone


def is_valid_phone(phone: str) -> bool:
    return bool(PHONE_PATTERN.match(phone))


def is_github_url(url: str | None) -> bool:
    if not url:
        return True
    return url.startswith("https://github.com/")
