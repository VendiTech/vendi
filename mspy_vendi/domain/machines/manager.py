from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import func, label, select

from mspy_vendi.core.manager import CRUDManager
from mspy_vendi.core.pagination import Page
from mspy_vendi.domain.geographies.models import Geography
from mspy_vendi.domain.machines.filters import MachineFilter
from mspy_vendi.domain.machines.models import Machine, MachineUser
from mspy_vendi.domain.machines.schemas import MachinesCountGeographySchema
from mspy_vendi.domain.user.models import User


class MachineManager(CRUDManager):
    sql_model = Machine

    async def get_machines_count_per_geography(
        self, query_filter: MachineFilter, user: User
    ) -> Page[MachinesCountGeographySchema]:
        """
        Get the count of machines located in the geography location.

        :param query_filter: Filter object.
        :param user: Current User.

        :return: Paginated list of machines count per geography.
        """
        stmt_machines_count = label("machines", func.count(self.sql_model.id))
        stmt_geography_object = func.jsonb_build_object(
            "id",
            Geography.id,
            "name",
            Geography.name,
            "postcode",
            Geography.postcode,
        ).label("geography")

        stmt = (
            select(stmt_machines_count, stmt_geography_object)
            .join(Geography, Geography.id == self.sql_model.geography_id)
            .group_by(Geography.id)
            .order_by(Geography.id)
        )

        if not user.is_superuser:
            stmt = stmt.join(MachineUser, MachineUser.machine_id == self.sql_model.id).where(
                MachineUser.user_id == user.id
            )

        stmt = query_filter.filter(stmt)

        return await paginate(self.session, stmt, unique=False)
