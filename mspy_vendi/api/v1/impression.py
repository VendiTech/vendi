from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import ORJSONResponse, Response, StreamingResponse
from fastapi_filter import FilterDepends

from mspy_vendi.config import config
from mspy_vendi.core.api import CRUDApi, basic_endpoints, basic_permissions
from mspy_vendi.core.enums import ApiTagEnum, ExportTypeEnum
from mspy_vendi.core.enums.date_range import DateRangeEnum, ScheduleEnum
from mspy_vendi.core.enums.export import ExportEntityTypeEnum
from mspy_vendi.core.pagination import Page
from mspy_vendi.deps import get_db_session
from mspy_vendi.domain.auth import get_current_user
from mspy_vendi.domain.impressions.filters import ExportImpressionFilter, GeographyFilter, ImpressionFilter
from mspy_vendi.domain.impressions.schemas import (
    AdvertPlayoutsStatisticsSchema,
    AdvertPlayoutsTimeFrameSchema,
    AverageExposureSchema,
    AverageImpressionsSchema,
    ExportImpressionDetailSchema,
    ExposurePerRangeSchema,
    ExposureStatisticSchema,
    GeographyImpressionsCountSchema,
    ImpressionCreateSchema,
    ImpressionDetailSchema,
    ImpressionsSalesPlayoutsConvertions,
    TimeFrameImpressionsByVenueSchema,
    TimeFrameImpressionsSchema,
)
from mspy_vendi.domain.impressions.service import ImpressionService
from mspy_vendi.domain.user.models import User
from mspy_vendi.domain.user.schemas import UserExistingSchedulesSchema
from mspy_vendi.domain.user.services import UserService

router = APIRouter(prefix="/impression", default_response_class=ORJSONResponse, tags=[ApiTagEnum.IMPRESSIONS])


@router.get("/impressions-per-range", response_model=Page[TimeFrameImpressionsSchema])
async def get__impressions_per_range(
    time_frame: DateRangeEnum,
    query_filter: Annotated[ImpressionFilter, FilterDepends(ImpressionFilter)],
    impression_service: Annotated[ImpressionService, Depends()],
    user: Annotated[User, Depends(get_current_user())],
) -> Page[TimeFrameImpressionsSchema]:
    return await impression_service.get_impressions_per_range(
        time_frame=time_frame,
        query_filter=query_filter,
        user=user,
    )


@router.get("/impressions-per-geography", response_model=Page[GeographyImpressionsCountSchema])
async def get__impressions_per_geography(
    query_filter: Annotated[ImpressionFilter, FilterDepends(ImpressionFilter)],
    impression_service: Annotated[ImpressionService, Depends()],
    user: Annotated[User, Depends(get_current_user())],
) -> Page[GeographyImpressionsCountSchema]:
    return await impression_service.get_impressions_per_geography(
        query_filter=query_filter,
        user=user,
    )


@router.get("/exposure", response_model=ExposureStatisticSchema)
async def get__exposure_statistic(
    query_filter: Annotated[ImpressionFilter, FilterDepends(ImpressionFilter)],
    impression_service: Annotated[ImpressionService, Depends()],
    user: Annotated[User, Depends(get_current_user())],
) -> ExposureStatisticSchema:
    return await impression_service.get_exposure(query_filter, user)


@router.get("/exposure-per-range", response_model=Page[ExposurePerRangeSchema])
async def get__exposure_per_range(
    time_frame: DateRangeEnum,
    query_filter: Annotated[ImpressionFilter, FilterDepends(ImpressionFilter)],
    impression_service: Annotated[ImpressionService, Depends()],
    user: Annotated[User, Depends(get_current_user())],
) -> Page[ExposurePerRangeSchema]:
    return await impression_service.get_exposure_per_range(time_frame, query_filter, user)


@router.get("/average-impressions", response_model=AverageImpressionsSchema)
async def get__average_impressions(
    query_filter: Annotated[ImpressionFilter, FilterDepends(ImpressionFilter)],
    impression_service: Annotated[ImpressionService, Depends()],
    user: Annotated[User, Depends(get_current_user())],
) -> AverageImpressionsSchema:
    return await impression_service.get_average_impressions_count(query_filter, user)


@router.get("/advert-playouts-per-range", response_model=Page[AdvertPlayoutsTimeFrameSchema])
async def get__advert_playouts_per_range(
    time_frame: DateRangeEnum,
    query_filter: Annotated[ImpressionFilter, FilterDepends(ImpressionFilter)],
    impression_service: Annotated[ImpressionService, Depends()],
    user: Annotated[User, Depends(get_current_user())],
) -> Page[AdvertPlayoutsTimeFrameSchema]:
    return await impression_service.get_advert_playouts_per_range(time_frame, query_filter, user)


@router.get("/advert-playouts", response_model=AdvertPlayoutsStatisticsSchema)
async def get__advert_playouts_statistic(
    query_filter: Annotated[ImpressionFilter, FilterDepends(ImpressionFilter)],
    impression_service: Annotated[ImpressionService, Depends()],
    user: Annotated[User, Depends(get_current_user())],
) -> AdvertPlayoutsStatisticsSchema:
    return await impression_service.get_advert_playouts(query_filter, user)


@router.get("/average-exposure", response_model=AverageExposureSchema)
async def get__average_exposure(
    query_filter: Annotated[ImpressionFilter, FilterDepends(ImpressionFilter)],
    impression_service: Annotated[ImpressionService, Depends()],
    user: Annotated[User, Depends(get_current_user())],
) -> AverageExposureSchema:
    return await impression_service.get_average_exposure(query_filter, user)


@router.get("/impressions-by-venue-per-range", response_model=Page[TimeFrameImpressionsByVenueSchema])
async def get__impressions_by_venue_per_range(
    time_frame: DateRangeEnum,
    query_filter: Annotated[ImpressionFilter, FilterDepends(ImpressionFilter)],
    impression_service: Annotated[ImpressionService, Depends()],
    user: Annotated[User, Depends(get_current_user())],
) -> Page[TimeFrameImpressionsByVenueSchema]:
    return await impression_service.get_impressions_by_venue_per_range(time_frame, query_filter, user)


@router.get("/month-on-month-summary", response_model=Page[ImpressionsSalesPlayoutsConvertions])
async def get__months_on_month_summary(
    query_filter: Annotated[ImpressionFilter, FilterDepends(ImpressionFilter)],
    impression_service: Annotated[ImpressionService, Depends()],
    user: Annotated[User, Depends(get_current_user())],
    time_frame: DateRangeEnum = DateRangeEnum.MONTH,
) -> Page[ImpressionsSalesPlayoutsConvertions]:
    return await impression_service.get_impressions_sales_playouts_convertion_per_range(time_frame, query_filter, user)


@router.post("/export", response_class=StreamingResponse)
async def post__export_impressions(
    export_type: ExportTypeEnum,
    query_filter: Annotated[ExportImpressionFilter, FilterDepends(ExportImpressionFilter)],
    impression_service: Annotated[ImpressionService, Depends()],
    user: Annotated[User, Depends(get_current_user())],
) -> StreamingResponse:
    return await impression_service.export(
        user=user,
        query_filter=query_filter,
        export_type=export_type,
        entity=ExportEntityTypeEnum.IMPRESSION,
    )


@router.get("/export-raw-data", response_model=Page[ExportImpressionDetailSchema])
async def get__impressions_export_raw_data(
    query_filter: Annotated[ExportImpressionFilter, FilterDepends(ExportImpressionFilter)],
    impression_service: Annotated[ImpressionService, Depends()],
    user: Annotated[User, Depends(get_current_user())],
) -> Page[ExportImpressionDetailSchema]:
    return await impression_service.get_export_data(query_filter, user)


@router.post("/schedule", response_class=StreamingResponse)
async def post__schedule_impressions(
    export_type: ExportTypeEnum,
    schedule: ScheduleEnum,
    query_filter: Annotated[GeographyFilter, FilterDepends(GeographyFilter)],
    user_service: Annotated[UserService, Depends()],
    user: Annotated[User, Depends(get_current_user())],
) -> Response:
    if schedule.MINUTELY and config.is_production:
        raise ValueError("Minutely schedule is not allowed")

    await user_service.schedule_export(
        user=user,,
        export_type=export_type,
        query_filter=query_filter,
        schedule=schedule,
        entity_type=ExportEntityTypeEnum.IMPRESSION,
    )

    return Response(status_code=status.HTTP_202_ACCEPTED)


@router.get("/schedule/view", tags=[ApiTagEnum.USER])
async def get__existing_schedules(
    user: Annotated[User, Depends(get_current_user())],
    service: Annotated[UserService, Depends()],
) -> list[UserExistingSchedulesSchema]:
    return await service.get_existing_schedules(user_id=user.id, entity_type=ExportEntityTypeEnum.IMPRESSION)


@router.delete("/schedule/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete__existing_schedule(
    schedule_id: str,
    user: Annotated[User, Depends(get_current_user())],
    service: Annotated[UserService, Depends()],
):
    return await service.delete_existing_schedule(
        user=user,
        schedule_id=schedule_id,
        entity_type=ExportEntityTypeEnum.IMPRESSION,
    )


class ImpressionAPI(CRUDApi):
    service = ImpressionService
    schema = ImpressionDetailSchema
    create_schema = ImpressionCreateSchema
    current_user_mapping = basic_permissions
    endpoints = basic_endpoints
    get_db_session = Depends(get_db_session)
    pagination_schema = Page
    api_tags = (ApiTagEnum.IMPRESSIONS,)


ImpressionAPI(router)
