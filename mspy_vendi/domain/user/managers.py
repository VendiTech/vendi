from mspy_vendi.core.manager import CRUDManager
from mspy_vendi.domain.user.models import User


class UserManager(CRUDManager):
    sql_model = User
