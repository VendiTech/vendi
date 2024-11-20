from datetime import date

from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import CTE, Date, cast, func, label, select, text
from sqlalchemy.dialects.postgresql import insert

from mspy_vendi.core.enums.date_range import DateRangeEnum
from mspy_vendi.core.manager import CRUDManager
from mspy_vendi.core.pagination import Page
from mspy_vendi.db import Impression
from mspy_vendi.domain.impressions.filters import ImpressionFilter
from mspy_vendi.domain.impressions.schemas import ImpressionCreateSchema, TimeFrameImpressionsSchema


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
                text(f"'1 {time_frame.value}'"),
            ).label("time_frame")
        ).cte("date_range")

    async def get_impressions_per_week(
        self, time_frame: DateRangeEnum, query_filter: ImpressionFilter
    ) -> Page[TimeFrameImpressionsSchema]:
        """
        Get the count of impressions grouped by week.

        :param time_frame: Time frame to group the data.
        :param query_filter: Filter object.

        :return: Total count of impression per week.
        """
        stmt_time_frame = label("time_frame", func.date_trunc(time_frame.value, self.sql_model.date))
        stmt_sum_impressions = label("impressions", func.count(self.sql_model.total_impressions))

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
