from mspy_vendi.core.manager import CRUDManager
from mspy_vendi.db import Sale


class SaleManager(CRUDManager):
    sql_model = Sale
