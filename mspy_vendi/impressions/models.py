from django.db import models

from mspy_vendi.core.models import BaseModel
from mspy_vendi.machines.models import Machine


class Impression(BaseModel):
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE)
    date = models.DateField()
    total_impressions = models.IntegerField()
    temperature = models.IntegerField()
    rainfall = models.IntegerField()
    source_system = models.CharField(max_length=50)
    source_system_id = models.IntegerField()

    class Meta:
        verbose_name = "Impression"
        verbose_name_plural = "Impressions"
        db_table = "impression"
