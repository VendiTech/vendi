from pydantic import PositiveInt

from mspy_vendi.core.filter import BaseFilter
from mspy_vendi.domain.user.models import User


class UserFilter(BaseFilter):
    id__in: list[PositiveInt] | None = None

    firstname: str | None = None
    lastname: str | None = None
    email: str | None = None
    company_name: str | None = None
    job_title: str | None = None
    phone_number: str | None = None

    # Multi-field search
    search: str | None = None

    order_by: list[str] | None = ["-id"]

    class Constants(BaseFilter.Constants):
        model = User
        fields_for_insensitive_search = ["firstname", "lastname", "email", "company_name", "job_title"]
        multi_search_fields = ["firstname", "lastname", "email"]
