from pydantic import PositiveInt

from mspy_vendi.core.filter import BaseFilter
from mspy_vendi.domain.user.enums import RoleEnum
from mspy_vendi.domain.user.models import User


class UserFilter(BaseFilter):
    id__in: list[PositiveInt] | None = None

    firstname: str | None = None
    lastname: str | None = None
    email: str | None = None
    company_name: str | None = None
    job_title: str | None = None
    phone_number: str | None = None
    role: RoleEnum | None = None

    #### Internal filters (JOIN on manager side ) ########
    machine_id__in: list[PositiveInt] | None = None
    geography_id__in: list[PositiveInt] | None = None

    product_id__in: list[PositiveInt] | None = None
    product_category_id__in: list[PositiveInt] | None = None
    #######################################################

    # Multi-field search
    search: str | None = None

    order_by: list[str] | None = ["-id"]

    class Constants(BaseFilter.Constants):
        model = User
        fields_for_insensitive_search = ["firstname", "lastname", "email", "company_name", "job_title"]
        multi_search_fields = ["firstname", "lastname", "email"]
        extra_order_by_fields = ["number_of_machines", "number_of_products"]
