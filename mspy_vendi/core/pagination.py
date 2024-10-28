from fastapi import Query
from fastapi_pagination import Page as FastAPIPaginationPage
from fastapi_pagination.customization import CustomizedPage, UseParamsFields

Page = CustomizedPage[
    FastAPIPaginationPage,
    UseParamsFields(size=Query(100, ge=1, le=1000)),
]
