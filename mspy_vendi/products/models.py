from django.db import models

from mspy_vendi.core.models import BaseModel


class ProductCategory(BaseModel):
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"<{self.__class__.__name__.capitalize()}>: {self.name}"

    class Meta:
        verbose_name = "Product Category"
        verbose_name_plural = "Product Categories"
        db_table = "product_category"


class Product(BaseModel):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"<{self.__class__.__name__.capitalize()}>: {self.name}"

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        db_table = "product"
