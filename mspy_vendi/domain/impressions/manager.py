from datetime import date

from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import CTE, Date, cast, func, label, select, text
from sqlalchemy.dialects.postgresql import insert

from mspy_vendi.core.enums.date_range import DateRangeEnum
from mspy_vendi.core.manager import CRUDManager
from mspy_vendi.core.pagination import Page
from mspy_vendi.db import Impression
from mspy_vendi.domain.geographies.models import Geography
from mspy_vendi.domain.impressions.filters import ExportImpressionFilter, ImpressionFilter
from mspy_vendi.domain.impressions.schemas import (
    AdvertPlayoutsBaseSchema,
    AverageExposureSchema,
    AverageImpressionsSchema,
    ExposurePerRangeSchema,
    GeographyDecimalImpressionTimeFrameSchema,
    GeographyImpressionsCountSchema,
    ImpressionCreateSchema,
    TimeFrameImpressionsSchema,
)
from mspy_vendi.domain.machine_impression.models import MachineImpression
from mspy_vendi.domain.machines.models import Machine


class ImpressionManager(CRUDManager):
    sql_model = Impression

    async def get_latest_impression_date(self, device_number: str) -> date | None:
        """
        Get the date of the latest impression in the database.

        :return: The date of the latest impression or None if no impressions are found.
        """
        stmt = (
            select(self.sql_model.date)
            .where(self.sql_model.device_number == device_number)
            .order_by(self.sql_model.date.desc())
            .limit(1)
        )

        return await self.session.scalar(stmt)

    async def create_batch(self, obj: list[ImpressionCreateSchema]) -> None:
        """
        Create a batch of impressions in the database.

        :param obj: A list of impressions to create.
        """
        try:
            stmt = insert(self.sql_model).on_conflict_do_nothing(index_elements=[self.sql_model.source_system_id])

            await self.session.execute(stmt, [item.model_dump() for item in obj])
            await self.session.commit()

        except Exception as ex:
            await self.session.rollback()
            raise ex

    @staticmethod
    def _generate_date_range_cte(time_frame: DateRangeEnum, query_filter: ImpressionFilter) -> CTE:
        """
        Generate CTE with date range.
        It uses generate_series function to generate a range of dates between date_from and date_to.

        :param time_frame: Time frame to group the data.
        :param query_filter: Filter object.

        :return: CTE with the date range.
        """
        return select(
            func.generate_series(
                func.date_trunc(time_frame.value, cast(query_filter.date_from, Date)),
                cast(query_filter.date_to, Date),
                text(f"'{time_frame.interval}'"),
            ).label("time_frame")
        ).cte()

    async def get_impressions_per_range(
        self, time_frame: DateRangeEnum, query_filter: ImpressionFilter
    ) -> Page[TimeFrameImpressionsSchema]:
        """
        Get the count of impressions grouped by week.

        :param time_frame: Time frame to group the data.
        :param query_filter: Filter object.

        :return: Total count of impression per week.
        """
        stmt_time_frame = label("time_frame", func.date_trunc(time_frame.value, self.sql_model.date))
        stmt_sum_impressions = label("impressions", func.sum(self.sql_model.total_impressions))

        stmt = select(stmt_time_frame, stmt_sum_impressions).group_by(stmt_time_frame).order_by(stmt_time_frame)

        stmt = query_filter.filter(stmt)
        stmt = stmt.subquery()

        date_range_cte = self._generate_date_range_cte(time_frame, query_filter)

        final_stmt = (
            select(date_range_cte.c.time_frame, func.coalesce(stmt.c.impressions, 0).label("impressions"))
            .select_from(date_range_cte)
            .outerjoin(stmt, stmt.c.time_frame == date_range_cte.c.time_frame)
            .order_by(date_range_cte.c.time_frame)
        )

        return await paginate(self.session, final_stmt)

    async def get_impressions_per_geography(
        self, query_filter: ImpressionFilter
    ) -> Page[GeographyImpressionsCountSchema]:
        """
        Get count of total impressions for each geography.

        :param query_filter: Filter object.
        :return: Total count of impressions per geography.
        """
        stmt_sum_total_impressions = label("impressions", func.sum(self.sql_model.total_impressions))
        stmt_geography_id = label("id", Geography.id)
        stmt_geography_name = label("name", Geography.name)
        stmt_geography_postcode = label("postcode", Geography.postcode)

        stmt = (
            select(
                stmt_sum_total_impressions,
                func.jsonb_build_object(
                    "id",
                    stmt_geography_id,
                    "name",
                    stmt_geography_name,
                    "postcode",
                    stmt_geography_postcode,
                ).label("geography"),
            )
            .join(MachineImpression, MachineImpression.impression_device_number == self.sql_model.device_number)
            .join(Machine, Machine.id == MachineImpression.machine_id)
            .join(Geography, Geography.id == Machine.geography_id)
            .group_by(Geography.id)
            .order_by(Geography.id)
        )

        stmt = query_filter.filter(stmt)

        return await paginate(self.session, stmt, unique=False)

    async def get_average_impressions_per_geography(
        self, time_frame: DateRangeEnum, query_filter: ImpressionFilter
    ) -> Page[GeographyDecimalImpressionTimeFrameSchema]:
        """
        Get the average count of total impressions for each geography.

        :param time_frame: Time frame to group the data.
        :param query_filter: Filter object.
        :return: Average count of impressions per geography.
        """
        stmt_time_frame = label("time_frame", func.date_trunc(time_frame.value, self.sql_model.date))
        stmt_avg_total_impressions = label("impressions", func.avg(self.sql_model.total_impressions))
        stmt_geography_object = func.jsonb_build_object(
            "id", Geography.id, "name", Geography.name, "postcode", Geography.postcode
        ).label("geography")

        stmt = (
            select(
                stmt_time_frame,
                stmt_avg_total_impressions,
                stmt_geography_object,
            )
            .join(MachineImpression, MachineImpression.impression_device_number == self.sql_model.device_number)
            .join(Machine, Machine.id == MachineImpression.machine_id)
            .join(Geography, Geography.id == Machine.geography_id)
            .group_by(stmt_time_frame, Geography.id)
            .order_by(stmt_time_frame)
        )

        stmt = query_filter.filter(stmt)
        stmt = stmt.subquery()

        date_range_cte = self._generate_date_range_cte(time_frame, query_filter)

        final_stmt = (
            select(
                func.jsonb_build_object(
                    "time_frame",
                    date_range_cte.c.time_frame,
                    "geographies",
                    func.array_agg(
                        func.jsonb_build_object(
                            "geography", stmt.c.geography, "impressions", func.coalesce(stmt.c.impressions, 0)
                        )
                    ),
                )
            )
            .select_from(date_range_cte)
            .outerjoin(stmt, stmt.c.time_frame == date_range_cte.c.time_frame)
            .where(stmt.c.geography.isnot(None))
            .group_by(date_range_cte.c.time_frame)
            .order_by(date_range_cte.c.time_frame)
        )

        return await paginate(self.session, final_stmt, unique=False)

    async def export(self, query_filter: ExportImpressionFilter) -> list[Impression]:
        """
        Export impression data. This method is used to export sales data in different formats.
        It returns a list of sales objects based on the filter.

        :param query_filter: Filter object.

        :return: List of sales objects.
        """
        stmt = (
            select(
                label("Impression ID", self.sql_model.id),
                label("Device Number", self.sql_model.device_number),
                label("Venue name", self.sql_model.source_system),
                label("Geography", Geography.name),
                label("Total Impressions", self.sql_model.total_impressions),
                label("Machine ID", Machine.id),
                label("Machine Name", Machine.name),
                label("Date", self.sql_model.date),
            )
            .select_from(self.sql_model)
            .outerjoin(MachineImpression, MachineImpression.impression_device_number == self.sql_model.device_number)
            .outerjoin(Machine, Machine.id == MachineImpression.machine_id)
            .outerjoin(Geography, Geography.id == Machine.geography_id)
            .order_by(self.sql_model.date)
        )

        if query_filter.geography_id__in:
            stmt = stmt.where(Geography.id.in_(query_filter.geography_id__in or []))
            setattr(query_filter, "geography_id__in", None)

        stmt = query_filter.filter(stmt)

        return (await self.session.execute(stmt)).mappings().all()  # type: ignore

    async def get_exposure(self, query_filter: ImpressionFilter) -> Page[ExposurePerRangeSchema]:
        """
        Get an exposure time and its corresponding date.

        :param query_filter: Filter object.
        :return: Paginated list with an exposure time (seconds) and a date.
        """
        stmt_second_exposure = label("seconds_exposure", func.sum(self.sql_model.seconds_exposure))
        stmt_time_frame = label("time_frame", self.sql_model.date)

        stmt = select(stmt_second_exposure, stmt_time_frame).group_by(stmt_time_frame).order_by(stmt_time_frame)

        stmt = query_filter.filter(stmt)

        return await paginate(self.session, stmt, unique=False)

    async def get_average_impressions_count(self, query_filter: ImpressionFilter) -> AverageImpressionsSchema:
        """
        Get average count of impressions per time range.

        :param query_filter: Filter object.
        :return: Average count of impressions and count of total impression for all time.
        """
        stmt_avg_impressions = label("avg_impressions", func.avg(self.sql_model.total_impressions))
        stmt_total_impressions = label("total_impressions", func.sum(self.sql_model.total_impressions))

        stmt = select(stmt_avg_impressions)

        stmt = query_filter.filter(stmt)
        stmt = stmt.subquery()

        final_stmt = select(stmt.c.avg_impressions, stmt_total_impressions).group_by(stmt.c.avg_impressions)

        result = await self.session.execute(final_stmt)
        row = result.one()

        return AverageImpressionsSchema(avg_impressions=row.avg_impressions, total_impressions=row.total_impressions)

    async def get_adverts_playout(self, query_filter: ImpressionFilter) -> AdvertPlayoutsBaseSchema:
        """
        Get total time of advert playouts.

        :param query_filter: Filter object.
        :return: Total time of advert playouts (seconds).
        """
        stmt_sum_advert_playouts = label("advert_playouts", func.sum(self.sql_model.advert_playouts))

        stmt = select(stmt_sum_advert_playouts)
        stmt = query_filter.filter(stmt)

        result = await self.session.execute(stmt)
        row = result.one()

        return AdvertPlayoutsBaseSchema(advert_playouts=row.advert_playouts)

    async def get_average_exposure(self, query_filter: ImpressionFilter) -> AverageExposureSchema:
        """
        Get an average time of exposure.

        :param query_filter: Filter object.
        :return: Average time of exposure (seconds).
        """
        stmt_avg_exposure = label("seconds_exposure", func.avg(self.sql_model.seconds_exposure))

        stmt = select(stmt_avg_exposure)
        stmt = query_filter.filter(stmt)

        result = await self.session.execute(stmt)
        row = result.one()

        return AverageExposureSchema(seconds_exposure=row.seconds_exposure)
