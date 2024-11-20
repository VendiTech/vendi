from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse
from fastapi_filter import FilterDepends

from mspy_vendi.core.api import CRUDApi, basic_endpoints, basic_permissions
from mspy_vendi.core.enums import ApiTagEnum
from mspy_vendi.core.enums.date_range import DateRangeEnum
from mspy_vendi.core.pagination import Page
from mspy_vendi.deps import get_db_session
from mspy_vendi.domain.sales.filter import SaleFilter
from mspy_vendi.domain.sales.schemas import (
    BaseQuantitySchema,
    CategoryProductQuantitySchema,
    CategoryTimeFrameSalesSchema,
    ConversionRateSchema,
    DecimalQuantitySchema,
    DecimalTimeFrameSalesSchema,
    GeographyDecimalQuantitySchema,
    SaleCreateSchema,
    SaleDetailSchema,
    TimeFrameSalesSchema,
    TimePeriodSalesCountSchema,
    UnitsTimeFrameSchema,
)
from mspy_vendi.domain.sales.service import SaleService

router = APIRouter(prefix="/sale", default_response_class=ORJSONResponse, tags=[ApiTagEnum.SALES])


@router.get("/quantity-by-products", response_model=BaseQuantitySchema)
async def get__quantity_by_product(
    query_filter: Annotated[SaleFilter, FilterDepends(SaleFilter)],
    sale_service: Annotated[SaleService, Depends()],
) -> BaseQuantitySchema:
    return await sale_service.get_sales_quantity_by_product(query_filter)


@router.get("/quantity-per-range", response_model=Page[TimeFrameSalesSchema])
async def get__sales_per_range(
    time_frame: DateRangeEnum,
    query_filter: Annotated[SaleFilter, FilterDepends(SaleFilter)],
    sale_service: Annotated[SaleService, Depends()],
) -> Page[TimeFrameSalesSchema]:
    return await sale_service.get_sales_quantity_per_range(time_frame, query_filter)


@router.get("/average-sales", response_model=DecimalQuantitySchema)
async def get__average_sales_across_machines(
    query_filter: Annotated[SaleFilter, FilterDepends(SaleFilter)],
    sale_service: Annotated[SaleService, Depends()],
) -> DecimalQuantitySchema:
    return await sale_service.get_average_sales_across_machines(query_filter)


@router.get("/average-sales-per-range", response_model=Page[DecimalTimeFrameSalesSchema])
async def get__average_sales_per_range(
    time_frame: DateRangeEnum,
    query_filter: Annotated[SaleFilter, FilterDepends(SaleFilter)],
    sale_service: Annotated[SaleService, Depends()],
) -> Page[DecimalTimeFrameSalesSchema]:
    return await sale_service.get_average_sales_per_range(time_frame, query_filter)


@router.get("/quantity-per-product", response_model=Page[CategoryProductQuantitySchema])
async def get__quantity_per_product(
    query_filter: Annotated[SaleFilter, FilterDepends(SaleFilter)],
    sale_service: Annotated[SaleService, Depends()],
) -> Page[CategoryProductQuantitySchema]:
    return await sale_service.get_sales_quantity_per_category(query_filter)


@router.get("/quantity-per-product-over-time", response_model=Page[CategoryTimeFrameSalesSchema])
async def get__quantity_per_product_over_time(
    query_filter: Annotated[SaleFilter, FilterDepends(SaleFilter)],
    sale_service: Annotated[SaleService, Depends()],
) -> Page[CategoryTimeFrameSalesSchema]:
    return await sale_service.get_sales_category_quantity_per_time_frame(query_filter)


@router.get("/sales-per-time-period", response_model=list[TimePeriodSalesCountSchema])
async def get__sales_per_time_period(
    query_filter: Annotated[SaleFilter, FilterDepends(SaleFilter)],
    sale_service: Annotated[SaleService, Depends()],
) -> list[TimePeriodSalesCountSchema]:
    return await sale_service.get_sales_count_per_time_period(query_filter)


@router.get("/units-sold", response_model=Page[UnitsTimeFrameSchema])
async def get__units_sold(
    query_filter: Annotated[SaleFilter, FilterDepends(SaleFilter)],
    sale_service: Annotated[SaleService, Depends()],
) -> Page[UnitsTimeFrameSchema]:
    return await sale_service.get_units_sold(query_filter)


@router.get("/quantity-per-geography", response_model=Page[GeographyDecimalQuantitySchema])
async def get__quantity_per_geography(
    query_filter: Annotated[SaleFilter, FilterDepends(SaleFilter)],
    sale_service: Annotated[SaleService, Depends()],
) -> Page[GeographyDecimalQuantitySchema]:
    return await sale_service.get_sales_quantity_per_geography(query_filter)


@router.get("/conversion-rate", response_model=ConversionRateSchema)
async def get__conversion_rate(
    query_filter: Annotated[SaleFilter, FilterDepends(SaleFilter)],
    sale_service: Annotated[SaleService, Depends()],
) -> ConversionRateSchema:
    return await sale_service.get_conversion_rate(query_filter)


class SaleAPI(CRUDApi):
    service = SaleService
    schema = SaleDetailSchema
    create_schema = SaleCreateSchema
    current_user_mapping = basic_permissions
    endpoints = basic_endpoints
    get_db_session = Depends(get_db_session)
    pagination_schema = Page
    api_tags = (ApiTagEnum.SALES,)


SaleAPI(router)
