from django.db import models

from mspy_vendi.brand_partners.models import BrandPartner
from mspy_vendi.core.models import BaseModel
from mspy_vendi.geographies.models import Geography


class Machine(BaseModel):
    name = models.CharField(max_length=255)
    geography = models.ForeignKey(Geography, on_delete=models.CASCADE)
    brand_partners = models.ManyToManyField(BrandPartner, related_name="machines", through="MachineBrandPartner")

    class Meta:
        verbose_name = "Machine"
        verbose_name_plural = "Machines"
        db_table = "machine"


class MachineBrandPartner(BaseModel):
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE)
    brand_partner = models.ForeignKey(BrandPartner, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("machine", "brand_partner")
        verbose_name = "Machine Brand Partner"
        verbose_name_plural = "Machine Brand Partners"
        db_table = "machine_brand_partner"
