import io
import random
import uuid
import os
from typing import cast

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
    BRIGHTNESS_RED_WEIGHT,
    BRIGHTNESS_GREEN_WEIGHT,
    BRIGHTNESS_BLUE_WEIGHT,
    BRIGHTNESS_DIVISOR,
    BRIGHTNESS_THRESHOLD,
    HEX_RED_START,
    HEX_RED_END,
    HEX_GREEN_START,
    HEX_GREEN_END,
    HEX_BLUE_START,
    HEX_BLUE_END,
    HEX_BASE
)
from users.models import User


def _hex_to_rgb(color: str) -> tuple[int, int, int]:
    color = color.lstrip("#")

    red = int(
        color[HEX_RED_START:HEX_RED_END],
        HEX_BASE,
    )
    green = int(
        color[HEX_GREEN_START:HEX_GREEN_END],
        HEX_BASE,
    )
    blue = int(
        color[HEX_BLUE_START:HEX_BLUE_END],
        HEX_BASE,
    )

    return red, green, blue


def _get_text_color(background_color: str) -> str:
    red, green, blue = _hex_to_rgb(background_color)

    brightness = (
        red * BRIGHTNESS_RED_WEIGHT +
        green * BRIGHTNESS_GREEN_WEIGHT +
        blue * BRIGHTNESS_BLUE_WEIGHT
    ) / BRIGHTNESS_DIVISOR

    if brightness >= BRIGHTNESS_THRESHOLD:
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
        font = cast(
            ImageFont.ImageFont,
            ImageFont.truetype(
                font_path,
                AVATAR_TEXT_FONT_SIZE,
            ),
        )
    except OSError:
        font = cast(
            ImageFont.ImageFont,
            ImageFont.load_default(),
        )

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
