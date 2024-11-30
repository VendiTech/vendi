from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import ORJSONResponse, Response, StreamingResponse
from fastapi_filter import FilterDepends

from mspy_vendi.core.api import CRUDApi, basic_endpoints, basic_permissions
from mspy_vendi.core.enums import ApiTagEnum, ExportTypeEnum
from mspy_vendi.core.enums.date_range import DateRangeEnum, ScheduleEnum
from mspy_vendi.core.enums.export import ExportEntityTypeEnum
from mspy_vendi.core.pagination import Page
from mspy_vendi.deps import get_db_session
from mspy_vendi.domain.auth import get_current_user
from mspy_vendi.domain.sales.filters import ExportSaleFilter, GeographyFilter, SaleFilter
from mspy_vendi.domain.sales.schemas import (
    BaseQuantitySchema,
    CategoryProductQuantityDateSchema,
    CategoryProductQuantitySchema,
    CategoryTimeFrameSalesSchema,
    ConversionRateSchema,
    DecimalQuantitySchema,
    DecimalTimeFrameSalesSchema,
    GeographyDecimalQuantitySchema,
    ProductsCountGeographySchema,
    SaleCreateSchema,
    SaleDetailSchema,
    TimeFrameSalesSchema,
    TimePeriodSalesCountSchema,
    TimePeriodSalesRevenueSchema,
    UnitsTimeFrameSchema,
    VenueSalesQuantitySchema,
)
from mspy_vendi.domain.sales.service import SaleService
from mspy_vendi.domain.user.models import User
from mspy_vendi.domain.user.schemas import UserExistingSchedulesSchema
from mspy_vendi.domain.user.services import UserService

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


@router.get("/sales-revenue-per-time-period", response_model=list[TimePeriodSalesRevenueSchema])
async def get__sales_revenue_per_time_period(
    query_filter: Annotated[SaleFilter, FilterDepends(SaleFilter)],
    sale_service: Annotated[SaleService, Depends()],
) -> list[TimePeriodSalesRevenueSchema]:
    return await sale_service.get_sales_revenue_per_time_period(query_filter)


@router.get("/units-sold", response_model=Page[UnitsTimeFrameSchema])
async def get__units_sold(
    time_frame: DateRangeEnum,
    query_filter: Annotated[SaleFilter, FilterDepends(SaleFilter)],
    sale_service: Annotated[SaleService, Depends()],
) -> Page[UnitsTimeFrameSchema]:
    return await sale_service.get_units_sold(time_frame, query_filter)


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


@router.get("/frequency-of-sales", response_model=list[TimePeriodSalesCountSchema])
async def get__frequency_of_sales(
    query_filter: Annotated[SaleFilter, FilterDepends(SaleFilter)],
    sale_service: Annotated[SaleService, Depends()],
) -> list[TimePeriodSalesCountSchema]:
    return await sale_service.get_daily_sales_count_per_time_period(query_filter)


@router.post("/export", response_class=StreamingResponse)
async def post__export_sales(
    export_type: ExportTypeEnum,
    query_filter: Annotated[ExportSaleFilter, FilterDepends(ExportSaleFilter)],
    sale_service: Annotated[SaleService, Depends()],
    _: Annotated[User, Depends(get_current_user())],
) -> StreamingResponse:
    return await sale_service.export(
        query_filter=query_filter,
        export_type=export_type,
        entity=ExportEntityTypeEnum.SALE,
    )


@router.post("/schedule", response_class=StreamingResponse)
async def post__schedule_sales(
    export_type: ExportTypeEnum,
    schedule: ScheduleEnum,
    query_filter: Annotated[GeographyFilter, FilterDepends(GeographyFilter)],
    user_service: Annotated[UserService, Depends()],
    user: Annotated[User, Depends(get_current_user())],
) -> Response:
    await user_service.schedule_export(
        user=user,
        export_type=export_type,
        query_filter=query_filter,
        schedule=schedule,
        entity_type=ExportEntityTypeEnum.SALE,
    )

    return Response(status_code=status.HTTP_202_ACCEPTED)


@router.get("/schedule/view")
async def get__existing_schedules(
    user: Annotated[User, Depends(get_current_user())],
    service: Annotated[UserService, Depends()],
) -> list[UserExistingSchedulesSchema]:
    return await service.get_existing_schedules(user_id=user.id, entity_type=ExportEntityTypeEnum.SALE)


@router.delete("/schedule/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete__existing_schedule(
    schedule_id: str,
    user: Annotated[User, Depends(get_current_user())],
    service: Annotated[UserService, Depends()],
):
    return await service.delete_existing_schedule(
        user_id=user.id,
        schedule_id=schedule_id,
        entity_type=ExportEntityTypeEnum.SALE,
    )


@router.get("/sales-quantity-by-venue", response_model=Page[VenueSalesQuantitySchema])
async def get__sales_quantity_by_venue(
    query_filter: Annotated[SaleFilter, FilterDepends(SaleFilter)],
    sale_service: Annotated[SaleService, Depends()],
) -> Page[VenueSalesQuantitySchema]:
    return await sale_service.get_sales_by_venue_over_time(query_filter)


@router.get("/sales-quantity-by-category", response_model=Page[CategoryProductQuantityDateSchema])
async def get__sales_quantity_by_category(
    query_filter: Annotated[SaleFilter, FilterDepends(SaleFilter)],
    sale_service: Annotated[SaleService, Depends()],
) -> Page[CategoryProductQuantityDateSchema]:
    return await sale_service.get_sales_quantity_by_category(query_filter)


@router.get("/average-products-per-geography", response_model=Page[ProductsCountGeographySchema])
async def get__average_products_count_per_geography(
    query_filter: Annotated[SaleFilter, FilterDepends(SaleFilter)],
    sale_service: Annotated[SaleService, Depends()],
) -> Page[ProductsCountGeographySchema]:
    return await sale_service.get_average_products_count_per_geography(query_filter)


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
