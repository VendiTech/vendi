from django.db import models

from mspy_vendi.core.models import BaseModel


class BrandPartner(BaseModel):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Brand Partner"
        verbose_name_plural = "Brand Partners"
        db_table = "brand_partner"
