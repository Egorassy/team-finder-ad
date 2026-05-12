from django.db import models

from team_finder.constants import SKILL_NAME_MAX_LENGTH


class Skill(models.Model):
    name = models.CharField(max_length=SKILL_NAME_MAX_LENGTH, unique=True)

    def __str__(self):
        return self.name
