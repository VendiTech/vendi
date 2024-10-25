from django.contrib import admin

from mspy_vendi.geographies.models import Geography


@admin.register(Geography)
class GeographyAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "postcode")  # Display additional fields
    search_fields = ("name", "postcode")
    ordering = ("-created_at",)  # Order by creation date, descending
    readonly_fields = ("deleted_at",)  # Mark these fields as read-only
