from pydantic import PositiveInt

from mspy_vendi.core.filter import BaseFilter
from mspy_vendi.domain.geographies.models import Geography


class GeographyFilter(BaseFilter):
    id__in: list[PositiveInt] | None = None

    name: str | None = None
    postcode: str | None = None

    # Multi-field search
    search: str | None = None

    order_by: list[str] | None = ["-id"]

    class Constants(BaseFilter.Constants):
        model = Geography
        fields_for_insensitive_search = ["name", "postcode"]
