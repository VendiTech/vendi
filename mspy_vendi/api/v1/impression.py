from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse
from fastapi_filter import FilterDepends

from mspy_vendi.core.api import CRUDApi, basic_endpoints, basic_permissions
from mspy_vendi.core.enums import ApiTagEnum
from mspy_vendi.core.enums.date_range import DateRangeEnum
from mspy_vendi.core.pagination import Page
from mspy_vendi.deps import get_db_session
from mspy_vendi.domain.impressions.filters import ImpressionFilter
from mspy_vendi.domain.impressions.schemas import (
    AdvertPlayoutsBaseSchema,
    AverageImpressionsSchema,
    ExposurePerRangeSchema,
    GeographyDecimalImpressionTimeFrameSchema,
    GeographyImpressionsCountSchema,
    ImpressionCreateSchema,
    ImpressionDetailSchema,
    TimeFrameImpressionsSchema,
)
from mspy_vendi.domain.impressions.service import ImpressionsService

router = APIRouter(prefix="/impression", default_response_class=ORJSONResponse, tags=[ApiTagEnum.IMPRESSIONS])


@router.get("/impressions-per-week", response_model=Page[TimeFrameImpressionsSchema])
async def get__impressions_per_week(
    query_filter: Annotated[ImpressionFilter, FilterDepends(ImpressionFilter)],
    impression_service: Annotated[ImpressionsService, Depends()],
) -> Page[TimeFrameImpressionsSchema]:
    return await impression_service.get_impressions_per_week(query_filter)


@router.get("/impressions-per-geography", response_model=Page[GeographyImpressionsCountSchema])
async def get__impressions_per_geography(
    query_filter: Annotated[ImpressionFilter, FilterDepends(ImpressionFilter)],
    impression_service: Annotated[ImpressionsService, Depends()],
) -> Page[GeographyImpressionsCountSchema]:
    return await impression_service.get_impressions_per_geography(query_filter)


@router.get("/average-impressions-per-geography", response_model=Page[GeographyDecimalImpressionTimeFrameSchema])
async def get__average_impressions_per_geography(
    time_frame: DateRangeEnum,
    query_filter: Annotated[ImpressionFilter, FilterDepends(ImpressionFilter)],
    impression_service: Annotated[ImpressionsService, Depends()],
) -> Page[GeographyDecimalImpressionTimeFrameSchema]:
    return await impression_service.get_average_impressions_per_geography(time_frame, query_filter)


@router.get("/exposure-per-range", response_model=Page[ExposurePerRangeSchema])
async def get__exposure_per_range(
    query_filter: Annotated[ImpressionFilter, FilterDepends(ImpressionFilter)],
    impression_service: Annotated[ImpressionsService, Depends()],
) -> Page[ExposurePerRangeSchema]:
    return await impression_service.get_exposure_per_range(query_filter)


@router.get("/average-impressions-per-range", response_model=AverageImpressionsSchema)
async def get__average_impressions_per_range(
    query_filter: Annotated[ImpressionFilter, FilterDepends(ImpressionFilter)],
    impression_service: Annotated[ImpressionsService, Depends()],
) -> AverageImpressionsSchema:
    return await impression_service.get_average_impressions_count_per_range(query_filter)


@router.get("/adverts-playout-per-range", response_model=AdvertPlayoutsBaseSchema)
async def get__adverts_playout_per_range(
    query_filter: Annotated[ImpressionFilter, FilterDepends(ImpressionFilter)],
    impression_service: Annotated[ImpressionsService, Depends()],
) -> AdvertPlayoutsBaseSchema:
    return await impression_service.get_adverts_playout_per_range(query_filter)


class ImpressionAPI(CRUDApi):
    service = ImpressionsService
    schema = ImpressionDetailSchema
    create_schema = ImpressionCreateSchema
    current_user_mapping = basic_permissions
    endpoints = basic_endpoints
    get_db_session = Depends(get_db_session)
    pagination_schema = Page
    api_tags = (ApiTagEnum.IMPRESSIONS,)


ImpressionAPI(router)
