from mspy_vendi.core.manager import CRUDManager
from mspy_vendi.db import Product


class ProductManager(CRUDManager):
    sql_model = Product
