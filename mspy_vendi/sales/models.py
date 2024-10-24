from django.db import models

from mspy_vendi.core.models import BaseModel
from mspy_vendi.machines.models import Machine
from mspy_vendi.products.models import Product


class Sale(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE)
    sale_date = models.DateField()
    sale_time = models.TimeField()
    quantity = models.IntegerField()
    source_system = models.CharField(max_length=50)
    source_system_id = models.BigIntegerField()

    class Meta:
        verbose_name = "Sale"
        verbose_name_plural = "Sales"
        db_table = "sale"
