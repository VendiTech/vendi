from fastapi_filter import FilterDepends, with_prefix
from pydantic import PositiveInt

from mspy_vendi.core.filter import BaseFilter
from mspy_vendi.domain.geographies.filters import GeographyFilter
from mspy_vendi.domain.machines.models import Machine


class MachineFilter(BaseFilter):
    id__in: list[PositiveInt] | None = None

    name: str | None = None
    geography_id: int | None = None
    geography: GeographyFilter | None = FilterDepends(with_prefix("geography", GeographyFilter))
    search: str | None = None

    order_by: list[str] | None = ["-id"]

    class Constants(BaseFilter.Constants):
        model = Machine
        fields_for_insensitive_search = ["name"]
        multi_search_fields = ["name", "geography__name"]
