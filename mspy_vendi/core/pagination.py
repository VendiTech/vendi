from fastapi import Query
from fastapi_pagination import Page as FastAPIPaginationPage
from fastapi_pagination.customization import CustomizedPage, UseParamsFields
from pydantic import NonNegativeInt

Page = CustomizedPage[
    FastAPIPaginationPage,
    UseParamsFields(size=Query(100, ge=1, le=1000)),
]


class ExtendedFastAPIPaginationPage(FastAPIPaginationPage):
    previous_month_statistic: NonNegativeInt | None = None


ExtendedPage = CustomizedPage[
    ExtendedFastAPIPaginationPage,
    UseParamsFields(size=Query(100, ge=1, le=1000)),
]
