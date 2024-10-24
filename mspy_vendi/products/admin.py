from django.contrib import admin

from mspy_vendi.products.models import Product, ProductCategory

admin.site.register(Product)
admin.site.register(ProductCategory)
