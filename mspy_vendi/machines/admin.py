from django.contrib import admin

from mspy_vendi.machines.models import Machine, MachineBrandPartner


@admin.register(Machine)
class MachineAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "geography", "created_at")
    list_filter = ("geography", "created_at")
    search_fields = ("geography__name",)
    readonly_fields = ("deleted_at",)


admin.site.register(MachineBrandPartner)
