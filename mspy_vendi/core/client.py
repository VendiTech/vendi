__all__ = ["RequestClient"]

import json
from typing import Any, Callable, Mapping

import httpx
from httpx._types import QueryParamTypes
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed, wait_random

from mspy_vendi.config import config
from mspy_vendi.core.exceptions.base_exception import RequestTimeoutError, raise_http_error


class RequestMetaClass(type):
    """
    Metaclass for manage the creation HTTP client instance within classes that use this metaclass.
    The __del__ method is not guaranteed to be called, and relying on it for resource cleanup is not recommended.
    That's why it has no responsibility for closing client instance.

    This metaclass ensures that only one asynchronous HTTP client instance is created and shared across all instances
    of classes using this metaclass.
    """

    _client: httpx.AsyncClient | None = None

    def __call__(cls, *args, **kwargs):
        timeout: httpx.Timeout = httpx.Timeout(
            config.request_client.default_connection_timeout,
            connect=config.request_client.max_connection_timeout,
        )
        event_hooks: Mapping[str, list[Callable]] = {"response": [cls.raise_on_4xx_5xx]}

        if cls._client is None:
            ssl_params: dict[str, Any] = {
                "verify": config.request_client.ssl_verify,
                "cert": (
                    config.request_client.cert_path,
                    config.request_client.key_path,
                )
                if config.request_client.ssl_verify
                else None,
            }

            cls._client = httpx.AsyncClient(
                timeout=timeout,
                event_hooks=event_hooks,
                **ssl_params,
            )

        return super().__call__(*args, **kwargs)

    @staticmethod
    async def raise_on_4xx_5xx(response: httpx.Response):
        """
        Httpx hook for raising the error for 4xx 5xx errors.
        """
        await response.aread()

        try:
            response.raise_for_status()
        except httpx.HTTPError:
            try:
                data: dict = response.json()
            except json.JSONDecodeError:
                data: dict = {"detail": response.text}

            raise_http_error(response.status_code, data)


class RequestClient(metaclass=RequestMetaClass):
    _client: httpx.AsyncClient | None

    @retry(
        retry=(retry_if_exception_type((httpx.ReadTimeout, httpx.ConnectTimeout))),
        wait=wait_fixed(2) + wait_random(0, 2),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    async def send_request_with_retry(self, connection: httpx.AsyncClient, request_data: dict):
        """
        Sends a request using the provided HTTP client connection with retry logic.

        This method attempts to send the request using the given HTTP client connection.
        If a ReadTimeout or ConnectTimeout exception is encountered, it retries the request
        up to a maximum of 3 attempts with a fixed wait of 2 seconds between each attempt,
        plus a random wait of up to 2 seconds.

        Reraise parameter allows us not to propagate tenacity.RetryError, but normally show
        the exception your code encountered.

        :param connection: The HTTP client connection to use for sending the request.
        :param request_data: The HTTP request data to be sent.
        """
        return await connection.request(**request_data)

    async def send_request(
        self,
        method: str,
        url: str,
        *,
        payload: dict | None = None,
        data: dict | None = None,
        headers: dict | None = None,
        params: QueryParamTypes | None = None,
        with_retry: bool = False,
    ):
        """
        Sends an HTTP request using the specified HTTP method to the given URL.

        :param method: The HTTP method for the request ('GET', 'POST')
        :param url:  The URL to send the request to
        :param payload:  The payload data to include in the request body.
        :param data: The data to include in the request form.
        :param params: The Query Params to include in the request url.
        :param headers: Additional HTTP headers to include in the request.
        :param with_retry: if True, request will retry. Default to False.

        :return httpx.Response: The HTTP response received from the server.
        :raises AttributeError: If the _client was not initialized properly
        """
        if not self._client:
            raise AttributeError("Client is not initialized")

        request_data: dict = {
            "method": method,
            "url": url,
            "headers": headers or {},
            "params": params,
            "auth": ...,
        }

        if payload:
            request_data["headers"].update({"Content-Type": "application/json"})
            request_data["json"] = payload

        elif data:
            request_data["data"] = data

        try:
            if with_retry:
                return await self.send_request_with_retry(connection=self._client, request_data=request_data)

            return await self._client.request(**request_data)

        except httpx.TimeoutException:
            raise RequestTimeoutError

    @classmethod
    async def close(cls) -> None:
        """
        Close the async HTTP client associated with the class

        Args:
            cls: the class instance

        This method closes the async HTTP client, if it exists.

        Example usage:
        >>> async def main():
        >>>    first_client = RequestClient()
        >>>    second_client = RequestClient()
        >>>    # These request clients share same _client
        >>>    await first_client.close()
        >>>    # The line above going to raise AttributeError
        >>>    await second_client.send_request("GET", "https://www.google.com")
        >>>    # However, if another client is created, first_client & second_client can be used again
        >>>    third_client = RequestClient()
        >>>    # The lines above will work correctly and won't raise AttributeError
        >>>    await first_client.send_request("GET", "https://www.google.com")
        >>>    await second_client.send_request("GET", "https://www.google.com")

        If the client has already been closed or was not created, this method has no effect
        """
        if cls._client:
            await cls._client.aclose()

            cls._client = None
