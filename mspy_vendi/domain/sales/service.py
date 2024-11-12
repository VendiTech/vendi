from mspy_vendi.core.service import CRUDService
from mspy_vendi.domain.sales.filters import SaleFilter
from mspy_vendi.domain.sales.manager import SaleManager


class SaleService(CRUDService):
    manager_class = SaleManager
    filter_class = SaleFilter
