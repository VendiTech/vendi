from mspy_vendi.core.service import CRUDService
from mspy_vendi.domain.products.filters import ProductFilter
from mspy_vendi.domain.products.manager import ProductManager


class ProductService(CRUDService):
    manager_class = ProductManager
    filter_class = ProductFilter
