from mspy_vendi.core.service import CRUDService
from mspy_vendi.domain.impressions.filters import ImpressionFilter
from mspy_vendi.domain.impressions.manager import ImpressionManager


class ImpressionsService(CRUDService):
    manager_class = ImpressionManager
    filter_class = ImpressionFilter
