import io
import random
import uuid
import os

from PIL import Image, ImageDraw, ImageFont
from django.core.files.base import ContentFile
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.conf import settings

from team_finder.constants import (
    AVATAR_BG_COLORS,
    AVATAR_IMAGE_SIZE,
    AVATAR_TEXT_COLOR_DARK,
    AVATAR_TEXT_COLOR_LIGHT,
    AVATAR_TEXT_FONT_SIZE,
)
from users.models import User


def _hex_to_rgb(color: str) -> tuple[int, int, int]:
    color = color.lstrip("#")
    return tuple(int(color[index:index + 2], 16) for index in (0, 2, 4))


def _get_text_color(background_color: str) -> str:
    red, green, blue = _hex_to_rgb(background_color)
    brightness = (red * 299 + green * 587 + blue * 114) / 1000

    if brightness >= 140:
        return AVATAR_TEXT_COLOR_DARK

    return AVATAR_TEXT_COLOR_LIGHT


def _build_avatar_bytes(initial: str) -> bytes:
    background_color = random.choice(AVATAR_BG_COLORS)

    image = Image.new(
        "RGB",
        (AVATAR_IMAGE_SIZE, AVATAR_IMAGE_SIZE),
        color=background_color,
    )
    draw = ImageDraw.Draw(image)

    font_path = os.path.join(
        settings.BASE_DIR,
        "static",
        "fonts",
        "Neue_Haas_Grotesk_Display_Pro_75_Bold.otf",
    )

    try:
        font = ImageFont.truetype(font_path, AVATAR_TEXT_FONT_SIZE)
    except OSError:
        font = ImageFont.load_default()

    text = (initial or "U")[0].upper()
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = (AVATAR_IMAGE_SIZE - text_width) / 2 - bbox[0]
    y = (AVATAR_IMAGE_SIZE - text_height) / 2 - bbox[1]

    draw.text(
        (x, y),
        text,
        fill=_get_text_color(background_color),
        font=font,
    )

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


@receiver(pre_save, sender=User)
def fill_avatar_before_save(sender, instance, **kwargs):
    if instance.avatar:
        return

    source_text = instance.name or instance.email or "U"
    avatar_bytes = _build_avatar_bytes(source_text)
    filename = f"{uuid.uuid4().hex}.png"

    instance.avatar.save(
        filename,
        ContentFile(avatar_bytes),
        save=False,
    )
