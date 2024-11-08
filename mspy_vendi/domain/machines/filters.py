from pydantic import NonNegativeInt

from mspy_vendi.core.filter import BaseFilter
from mspy_vendi.domain.machines.models import Machine


class MachineFilter(BaseFilter):
    id__in: list[NonNegativeInt] | None = None

    name: str | None = None
    geography_id: int | None = None

    # Multi-field search
    search: str | None = None

    order_by: list[str] | None = ["-id"]

    class Constants(BaseFilter.Constants):
        model = Machine
        fields_for_insensitive_search = ["name", "geography_id"]
