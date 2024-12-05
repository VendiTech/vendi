from typing import Any

from sqlalchemy import VARCHAR, Select, case, cast, func, label, null, select
from sqlalchemy.orm import joinedload

from mspy_vendi.core.manager import CRUDManager
from mspy_vendi.domain.activity_log.filters import ActivityLogFilter
from mspy_vendi.domain.activity_log.models import ActivityLog
from mspy_vendi.domain.user.models import User


class ActivityLogManager(CRUDManager):
    sql_model = ActivityLog

    def get_query(self) -> Select:
        return super().get_query().options(joinedload(self.sql_model.user))

    async def export(self, query_filter: ActivityLogFilter, *_: Any) -> list[ActivityLog]:
        """
        Export activity_log data.
        This method is used to export activity_log data in different formats.
        It returns a list of sales objects based on the filter.

        :param query_filter: Filter object.

        :return: List of sales objects.
        """
        stmt = (
            select(
                label(
                    "ID",
                    case(
                        (self.sql_model.user_id.is_(null()), "Deleted"),
                        else_=cast(self.sql_model.user_id, VARCHAR),
                    ),
                ),
                label("Action", self.sql_model.event_type),
                label(
                    "Name",
                    case(
                        (User.firstname.is_(null()), "Deleted User"),
                        else_=func.concat(User.firstname, " ", User.lastname),
                    ),
                ),
                label("Date and time", cast(self.sql_model.created_at, VARCHAR)),
                label("Additional Context", self.sql_model.event_context),
            )
            .outerjoin(User, self.sql_model.user_id == User.id)
            .order_by(self.sql_model.created_at)
        )

        stmt = query_filter.filter(stmt, autojoin=False)

        return (await self.session.execute(stmt)).mappings().all()  # type: ignore
