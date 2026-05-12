import re


GITHUB_URL_REGEX = r"^https?:\/\/(www\.)?github\.com\/[\w\-\.]+(\/[\w\-\.]+)?\/?$"


def is_valid_github_url(url: str) -> bool:
    if not url:
        return True
    return bool(re.match(GITHUB_URL_REGEX, url))
