from mspy_vendi.core.service import CRUDService
from mspy_vendi.domain.geographies.filters import GeographyFilter
from mspy_vendi.domain.geographies.manager import GeographyManager


class GeographyService(CRUDService):
    manager_class = GeographyManager
    filter_class = GeographyFilter
