from django.db import models


class BaseModel(models.Model):
    """Base model for all models in the application."""

    id = models.BigAutoField(primary_key=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"<{self.__class__.__name__.capitalize()}>: {self.id}"

    class Meta:
        abstract = True
