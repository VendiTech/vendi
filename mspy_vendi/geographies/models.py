from django.db import models

from mspy_vendi.core.models import BaseModel


class Geography(BaseModel):
    name = models.CharField(max_length=255)
    postcode = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"<{self.__class__.__name__.capitalize()}>: {self.name}"

    class Meta:
        verbose_name = "Geography"
        verbose_name_plural = "Geographies"
        db_table = "geography"
