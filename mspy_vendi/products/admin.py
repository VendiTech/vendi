from django.contrib import admin

from mspy_vendi.products.models import Product, ProductCategory


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "category", "created_at")  # Display additional fields
    list_filter = ("category", "price", "created_at")  # Add a filter by category
    search_fields = ("name", "category__name")  # Enable search by product name
    ordering = ("-created_at",)  # Order by creation date, descending
    fieldsets = (
        ("Basic Information", {"fields": ("name", "category", "price")}),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),  # Collapse this section by default
            },
        ),
    )
    readonly_fields = ("created_at", "updated_at", "deleted_at")  # Mark these fields as read-only


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")  # Display additional fields
    search_fields = ("name",)
    ordering = ("-created_at",)  # Order by creation date, descending
    readonly_fields = ("deleted_at",)  # Mark these fields as read-only
