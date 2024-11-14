from sqlalchemy import Select, func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError

from mspy_vendi.core.manager import CRUDManager
from mspy_vendi.db import MachineImpression
from mspy_vendi.domain.machine_impression.schemas import (
    MachineImpressionBulkCreateResponseSchema,
    MachineImpressionCreateSchema,
)


class MachineImpressionManager(CRUDManager):
    sql_model = MachineImpression

    async def create_batch(self, obj: list[MachineImpressionCreateSchema]) -> MachineImpressionBulkCreateResponseSchema:
        """
        Create a batch of impressions in the database.
        If the record already exists, we will skip it. Due to the CONFLICT DO NOTHING clause.
        If the FK constraint fails, we will skip the record.

        We return the number of records that were created.

        :param obj: A list of impressions to create.

        :return: MachineImpressionBulkCreateResponseSchema
        """
        count_stmt: Select = select(func.count()).select_from(self.sql_model)
        existing_records: list[int] = await self.session.scalar(count_stmt)

        for item in obj:
            dict_item = item.model_dump()

            if not all(item.model_dump(exclude_defaults=True).values()):
                continue

            try:
                stmt = (
                    insert(self.sql_model)
                    .values(**dict_item)
                    .on_conflict_do_nothing(constraint="uq_machine_impression_machine_id_impression_device_number")
                )

                await self.session.execute(stmt)
                await self.session.commit()

            except IntegrityError:
                await self.session.rollback()
                continue

            except Exception as ex:
                await self.session.rollback()
                raise ex

        updated_records: list[int] = await self.session.scalar(count_stmt)

        return MachineImpressionBulkCreateResponseSchema(
            initial_records=existing_records, final_records=updated_records
        )
