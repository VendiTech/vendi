from datetime import date, time

from pydantic import PositiveInt

from mspy_vendi.core.constants import DEFAULT_SOURCE_SYSTEM
from mspy_vendi.core.schemas import BaseSchema


class CreateSaleSchema(BaseSchema):
    sale_date: date
    sale_time: time
    quantity: PositiveInt
    source_system: str = DEFAULT_SOURCE_SYSTEM
    source_system_id: PositiveInt
    product_id: PositiveInt
    machine_id: PositiveInt
