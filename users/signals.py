import random
from PIL import Image, ImageDraw

from django.db.models.signals import post_save
from django.dispatch import receiver

from users.models import User
from team_finder.constants import AVATAR_BG_COLORS


def generate_avatar(initial: str, size=200):
    color = random.choice(AVATAR_BG_COLORS)

    img = Image.new("RGB", (size, size), color=color)
    draw = ImageDraw.Draw(img)

    text = initial.upper()

    draw.text((size // 2 - 20, size // 2 - 20), text, fill="white")

    return img


@receiver(post_save, sender=User)
def create_avatar(sender, instance: User, created, **kwargs):
    if created and not instance.avatar:
        avatar = generate_avatar(instance.name[0])
        instance.avatar.save(f"{instance.pk}.png", avatar, save=True)
