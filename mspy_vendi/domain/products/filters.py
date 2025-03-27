from pydantic import PositiveInt

from mspy_vendi.core.filter import BaseFilter
from mspy_vendi.domain.products.models import Product


class ProductFilter(BaseFilter):
    id__in: list[PositiveInt] | None = None

    name: str | None = None
    product_category_id__in: list[PositiveInt] | None = None

    order_by: list[str] | None = ["-id"]

    class Constants(BaseFilter.Constants):
        model = Product
