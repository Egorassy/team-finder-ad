import re


def normalize_phone(phone: str) -> str:
    phone = phone.replace("+7", "8")
    return phone