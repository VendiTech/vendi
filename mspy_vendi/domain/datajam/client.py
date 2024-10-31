from mspy_vendi.config import config
from mspy_vendi.core.client import RequestClient


class NayaxClient:
    base_url: str = config.datajam.url

    def __init__(self):
        self.client = RequestClient()
