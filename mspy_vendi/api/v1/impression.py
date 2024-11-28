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
    AverageExposureSchema,
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


@router.get("/impressions-per-range", response_model=Page[TimeFrameImpressionsSchema])
async def get__impressions_per_range(
    time_frame: DateRangeEnum,
    query_filter: Annotated[ImpressionFilter, FilterDepends(ImpressionFilter)],
    impression_service: Annotated[ImpressionsService, Depends()],
) -> Page[TimeFrameImpressionsSchema]:
    return await impression_service.get_impressions_per_range(time_frame, query_filter)


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


@router.get("/exposure", response_model=Page[ExposurePerRangeSchema])
async def get__exposure(
    query_filter: Annotated[ImpressionFilter, FilterDepends(ImpressionFilter)],
    impression_service: Annotated[ImpressionsService, Depends()],
) -> Page[ExposurePerRangeSchema]:
    return await impression_service.get_exposure(query_filter)


@router.get("/average-impressions", response_model=AverageImpressionsSchema)
async def get__average_impressions(
    query_filter: Annotated[ImpressionFilter, FilterDepends(ImpressionFilter)],
    impression_service: Annotated[ImpressionsService, Depends()],
) -> AverageImpressionsSchema:
    return await impression_service.get_average_impressions_count(query_filter)


@router.get("/adverts-playout", response_model=AdvertPlayoutsBaseSchema)
async def get__adverts_playout(
    query_filter: Annotated[ImpressionFilter, FilterDepends(ImpressionFilter)],
    impression_service: Annotated[ImpressionsService, Depends()],
) -> AdvertPlayoutsBaseSchema:
    return await impression_service.get_adverts_playout(query_filter)


@router.get("/average-exposure", response_model=AverageExposureSchema)
async def get__average_exposure(
    query_filter: Annotated[ImpressionFilter, FilterDepends(ImpressionFilter)],
    impression_service: Annotated[ImpressionsService, Depends()],
) -> AverageExposureSchema:
    return await impression_service.get_average_exposure(query_filter)


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
