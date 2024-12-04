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
    CategoryProductQuantityDateSchema,
    CategoryProductQuantitySchema,
    CategoryTimeFrameSalesSchema,
    ConversionRateSchema,
    DecimalQuantityStatisticSchema,
    DecimalTimeFrameSalesSchema,
    GeographyDecimalQuantitySchema,
    ProductsCountGeographySchema,
    ProductVenueSalesCountSchema,
    QuantityStatisticSchema,
    SaleCreateSchema,
    SaleDetailSchema,
    TimeFrameSalesSchema,
    TimePeriodSalesCountSchema,
    TimePeriodSalesRevenueSchema,
    UnitsStatisticSchema,
    UnitsTimeFrameSchema,
    VenueSalesQuantitySchema,
)
from mspy_vendi.domain.sales.service import SaleService
from mspy_vendi.domain.user.models import User
from mspy_vendi.domain.user.schemas import UserExistingSchedulesSchema
from mspy_vendi.domain.user.services import UserService

router = APIRouter(prefix="/sale", default_response_class=ORJSONResponse, tags=[ApiTagEnum.SALES])


@router.get("/quantity-by-products", response_model=QuantityStatisticSchema)
async def get__quantity_by_product(
    query_filter: Annotated[SaleFilter, FilterDepends(SaleFilter)],
    sale_service: Annotated[SaleService, Depends()],
    user: Annotated[User, Depends(get_current_user())],
) -> QuantityStatisticSchema:
    return await sale_service.get_sales_quantity_by_product(query_filter, user)


@router.get("/quantity-per-range", response_model=Page[TimeFrameSalesSchema])
async def get__sales_per_range(
    time_frame: DateRangeEnum,
    query_filter: Annotated[SaleFilter, FilterDepends(SaleFilter)],
    sale_service: Annotated[SaleService, Depends()],
    user: Annotated[User, Depends(get_current_user())],
) -> Page[TimeFrameSalesSchema]:
    return await sale_service.get_sales_quantity_per_range(time_frame, query_filter, user)


@router.get("/average-sales", response_model=DecimalQuantityStatisticSchema)
async def get__average_sales_across_machines(
    query_filter: Annotated[SaleFilter, FilterDepends(SaleFilter)],
    sale_service: Annotated[SaleService, Depends()],
    user: Annotated[User, Depends(get_current_user())],
) -> DecimalQuantityStatisticSchema:
    return await sale_service.get_average_sales_across_machines(query_filter, user)


@router.get("/average-sales-per-range", response_model=Page[DecimalTimeFrameSalesSchema])
async def get__average_sales_per_range(
    time_frame: DateRangeEnum,
    query_filter: Annotated[SaleFilter, FilterDepends(SaleFilter)],
    sale_service: Annotated[SaleService, Depends()],
    user: Annotated[User, Depends(get_current_user())],
) -> Page[DecimalTimeFrameSalesSchema]:
    return await sale_service.get_average_sales_per_range(time_frame, query_filter, user)


@router.get("/quantity-per-product", response_model=Page[CategoryProductQuantitySchema])
async def get__quantity_per_product(
    query_filter: Annotated[SaleFilter, FilterDepends(SaleFilter)],
    sale_service: Annotated[SaleService, Depends()],
    user: Annotated[User, Depends(get_current_user())],
) -> Page[CategoryProductQuantitySchema]:
    return await sale_service.get_sales_quantity_per_category(query_filter, user)


@router.get("/quantity-per-category", response_model=Page[CategoryTimeFrameSalesSchema])
async def get__quantity_per_category(
    query_filter: Annotated[SaleFilter, FilterDepends(SaleFilter)],
    sale_service: Annotated[SaleService, Depends()],
    user: Annotated[User, Depends(get_current_user())],
) -> Page[CategoryTimeFrameSalesSchema]:
    return await sale_service.get_sales_category_quantity_per_time_frame(query_filter, user)


@router.get("/sales-revenue-per-time-period", response_model=list[TimePeriodSalesRevenueSchema])
async def get__sales_revenue_per_time_period(
    query_filter: Annotated[SaleFilter, FilterDepends(SaleFilter)],
    sale_service: Annotated[SaleService, Depends()],
    user: Annotated[User, Depends(get_current_user())],
) -> list[TimePeriodSalesRevenueSchema]:
    return await sale_service.get_sales_revenue_per_time_period(query_filter, user)


@router.get("/units-sold-per-range", response_model=Page[UnitsTimeFrameSchema])
async def get__units_sold(
    time_frame: DateRangeEnum,
    query_filter: Annotated[SaleFilter, FilterDepends(SaleFilter)],
    sale_service: Annotated[SaleService, Depends()],
    user: Annotated[User, Depends(get_current_user())],
) -> Page[UnitsTimeFrameSchema]:
    return await sale_service.get_units_sold_per_range(time_frame, query_filter, user)


@router.get("/units-sold-statistic", response_model=UnitsStatisticSchema)
async def get__units_sold_statistic(
    query_filter: Annotated[SaleFilter, FilterDepends(SaleFilter)],
    sale_service: Annotated[SaleService, Depends()],
    user: Annotated[User, Depends(get_current_user())],
) -> UnitsStatisticSchema:
    return await sale_service.get_units_sold_statistic(query_filter, user)


@router.get("/quantity-per-geography", response_model=Page[GeographyDecimalQuantitySchema])
async def get__quantity_per_geography(
    query_filter: Annotated[SaleFilter, FilterDepends(SaleFilter)],
    sale_service: Annotated[SaleService, Depends()],
    user: Annotated[User, Depends(get_current_user())],
) -> Page[GeographyDecimalQuantitySchema]:
    return await sale_service.get_sales_quantity_per_geography(query_filter, user)


@router.get("/conversion-rate", response_model=ConversionRateSchema)
async def get__conversion_rate(
    query_filter: Annotated[SaleFilter, FilterDepends(SaleFilter)],
    sale_service: Annotated[SaleService, Depends()],
    user: Annotated[User, Depends(get_current_user())],
) -> ConversionRateSchema:
    return await sale_service.get_conversion_rate(query_filter, user)


@router.get("/frequency-of-sales", response_model=list[TimePeriodSalesCountSchema])
async def get__frequency_of_sales(
    query_filter: Annotated[SaleFilter, FilterDepends(SaleFilter)],
    sale_service: Annotated[SaleService, Depends()],
    user: Annotated[User, Depends(get_current_user())],
) -> list[TimePeriodSalesCountSchema]:
    return await sale_service.get_daily_sales_count_per_time_period(query_filter, user)


@router.get("/sales-quantity-by-venue", response_model=Page[VenueSalesQuantitySchema])
async def get__sales_quantity_by_venue(
    query_filter: Annotated[SaleFilter, FilterDepends(SaleFilter)],
    sale_service: Annotated[SaleService, Depends()],
    user: Annotated[User, Depends(get_current_user())],
) -> Page[VenueSalesQuantitySchema]:
    return await sale_service.get_sales_by_venue_over_time(query_filter, user)


@router.get("/sales-quantity-by-category", response_model=Page[CategoryProductQuantityDateSchema])
async def get__sales_quantity_by_category(
    query_filter: Annotated[SaleFilter, FilterDepends(SaleFilter)],
    sale_service: Annotated[SaleService, Depends()],
    user: Annotated[User, Depends(get_current_user())],
) -> Page[CategoryProductQuantityDateSchema]:
    return await sale_service.get_sales_quantity_by_category(query_filter, user)


@router.get("/average-products-per-geography", response_model=Page[ProductsCountGeographySchema])
async def get__average_products_count_per_geography(
    query_filter: Annotated[SaleFilter, FilterDepends(SaleFilter)],
    sale_service: Annotated[SaleService, Depends()],
    user: Annotated[User, Depends(get_current_user())],
) -> Page[ProductsCountGeographySchema]:
    return await sale_service.get_average_products_count_per_geography(query_filter, user)


@router.get("/products-quantity-by-venue", response_model=Page[ProductVenueSalesCountSchema])
async def get__products_quantity_by_venue(
    query_filter: Annotated[SaleFilter, FilterDepends(SaleFilter)],
    sale_service: Annotated[SaleService, Depends()],
    user: Annotated[User, Depends(get_current_user())],
) -> Page[ProductVenueSalesCountSchema]:
    return await sale_service.get_products_quantity_by_venue(query_filter, user)


@router.post("/export", response_class=StreamingResponse)
async def post__export_sales(
    export_type: ExportTypeEnum,
    query_filter: Annotated[ExportSaleFilter, FilterDepends(ExportSaleFilter)],
    sale_service: Annotated[SaleService, Depends()],
    user: Annotated[User, Depends(get_current_user())],
) -> StreamingResponse:
    return await sale_service.export(
        query_filter=query_filter,
        export_type=export_type,
        entity=ExportEntityTypeEnum.SALE,
        user=user,
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
        user=user,
        schedule_id=schedule_id,
        entity_type=ExportEntityTypeEnum.SALE,
    )


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
