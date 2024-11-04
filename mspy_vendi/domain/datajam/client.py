import httpx

from mspy_vendi.config import config
from mspy_vendi.core.client import RequestClient
from mspy_vendi.core.enums import RequestMethodEnum
from mspy_vendi.domain.datajam.schemas import DataJamImpressionSchema, DataJamRequestSchema


class DataJamClient:
    base_url: str = config.datajam.url

    def __init__(self):
        self.auth_credentials = httpx.BasicAuth(username=config.datajam.username, password=config.datajam.password)
        self.client = RequestClient()

    async def get_impressions(self, request_data: DataJamRequestSchema) -> DataJamImpressionSchema:
        """
        Returns impression data from DataJam API

        :param request_data: The request data to be sent.

        :return DataJamImpressionSchema: The response data from the server.
        """
        response = await self.client.send_request(
            RequestMethodEnum.GET,
            url=self.base_url,
            payload=request_data.model_dump(),
            auth=self.auth_credentials,
        )

        return DataJamImpressionSchema.model_validate(response.json())
