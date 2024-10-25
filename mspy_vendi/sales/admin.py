from django.contrib import admin

from mspy_vendi.sales.models import Sale


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "machine", "sale_date", "sale_time", "quantity")
    list_filter = ("sale_date", "product", "machine")
    search_fields = ("id", "product__name", "product__id", "machine__name", "machine__id")
    ordering = ("-sale_date",)
