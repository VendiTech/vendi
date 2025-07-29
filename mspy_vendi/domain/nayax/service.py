from sqlalchemy.ext.asyncio import AsyncSession

from mspy_vendi.config import log
from mspy_vendi.core.helpers.db_helpers import serialize_for_json
from mspy_vendi.domain.entity_log.enums import EntityTypeEnum
from mspy_vendi.domain.entity_log.manager import EntityLogManager
from mspy_vendi.domain.entity_log.schemas import EntityLogCreateSchema
from mspy_vendi.domain.geographies.manager import GeographyManager
from mspy_vendi.domain.geographies.schemas import GeographyCreateSchema
from mspy_vendi.domain.machines.manager import MachineManager
from mspy_vendi.domain.machines.schemas import MachineCreateSchema
from mspy_vendi.domain.nayax.schemas import NayaxTransactionSchema
from mspy_vendi.domain.product_category.manager import ProductCategoryManager
from mspy_vendi.domain.product_category.schemas import CreateProductCategorySchema
from mspy_vendi.domain.products.manager import ProductManager
from mspy_vendi.domain.products.schemas import ProductCreateSchema
from mspy_vendi.domain.sales.manager import SaleManager
from mspy_vendi.domain.sales.schemas import SaleCreateSchema


class NayaxService:
    def __init__(self, db_session: AsyncSession):
        self.geography_manager = GeographyManager(db_session)
        self.machine_manager = MachineManager(db_session)
        self.product_manager = ProductManager(db_session)
        self.product_category_manager = ProductCategoryManager(db_session)
        self.sale_manager = SaleManager(db_session)
        self.entity_log_manager = EntityLogManager(db_session)

    async def process_message(self, message: NayaxTransactionSchema) -> None:
        geography, old_geography, is_updated = await self.geography_manager.update_or_create(
            name=message.data.area_description or message.data.actor_description,
            obj=GeographyCreateSchema(
                name=message.data.area_description or message.data.actor_description,
                postcode=str(message.data.location_code or message.data.actor_code),
            ),
        )

        log.info("Geography object", geography_name=geography.name, is_updated=is_updated)

        if is_updated:
            await self.entity_log_manager.create(
                obj=EntityLogCreateSchema(
                    entity_type=EntityTypeEnum.GEOGRAPHY,
                    old_value=serialize_for_json(old_geography.to_dict()),
                    new_value=serialize_for_json(geography.to_dict()),
                )
            )
            log.info("Updated data:", old_geography=old_geography.to_dict(), geography=geography.to_dict())

        machine, old_machine, is_updated = await self.machine_manager.update_or_create(
            obj_id=message.machine_id,
            obj=MachineCreateSchema(
                name=message.data.machine_name,
                geography_id=geography.id,
            ),
        )

        log.info("Machine object", machine_id=machine.id, is_updated=is_updated)

        if is_updated:
            await self.entity_log_manager.create(
                obj=EntityLogCreateSchema(
                    entity_type=EntityTypeEnum.MACHINE,
                    old_value=serialize_for_json(old_machine.to_dict()),
                    new_value=serialize_for_json(machine.to_dict()),
                ),
            )
            log.info("Updated data", old_machine=old_machine.to_dict(), machine=machine.to_dict())

        for product_item in message.data.products:
            log.info("Start working with the following product", product_id=product_item.product_id)

            product_category, old_product_category, is_updated = await self.product_category_manager.update_or_create(
                name=product_item.product_group,
                obj=CreateProductCategorySchema(name=product_item.product_group),
            )

            if is_updated:
                await self.entity_log_manager.create(
                    obj=EntityLogCreateSchema(
                        entity_type=EntityTypeEnum.PRODUCT_CATEGORY,
                        old_value=serialize_for_json(old_product_category.to_dict()),
                        new_value=serialize_for_json(product_category.to_dict()),
                    )
                )
                log.info(
                    "Updated data",
                    product_category=product_category.to_dict(),
                    old_product_category=old_product_category.to_dict(),
                )

            log.info(
                "Product category object",
                product_category_name=product_category.name,
                is_updated=is_updated,
            )

            log.info(
                "Provided Product object",
                product_id=product_item.product_id,
                price=product_item.product_bruto,
            )

            product, old_product, is_updated = await self.product_manager.update_or_create(
                obj_id=product_item.product_id,
                obj=ProductCreateSchema(
                    name=product_item.product_name,
                    price=product_item.product_bruto,
                    product_category_id=product_category.id,
                ),
            )

            log.info("Product object", product_id=product.id, is_updated=is_updated)

            if is_updated:
                await self.entity_log_manager.create(
                    obj=EntityLogCreateSchema(
                        entity_type=EntityTypeEnum.PRODUCT,
                        old_value=serialize_for_json(old_product.to_dict()),
                        new_value=serialize_for_json(product.to_dict()),
                    )
                )
                log.info("Updated data", product=product.to_dict(), old_product=old_product.to_dict())

            log.info(
                "Provided Sale object",
                sale_id=message.transaction_id,
                quantity=product_item.product_quantity,
                source_system_id=message.transaction_id,
            )
            sale_datetime = message.machine_time or message.data.machine_au_time
            sale, old_sale, is_updated = await self.sale_manager.update_or_create(
                obj_id=message.transaction_id,
                obj=SaleCreateSchema(
                    sale_date=sale_datetime.date(),
                    sale_time=sale_datetime.time(),
                    quantity=product_item.product_quantity or 1,
                    source_system_id=message.transaction_id,
                    product_id=product.id,
                    machine_id=machine.id,
                ),
            )

            log.info("Sale object", sale_id=sale.id, is_updated=is_updated)

            if is_updated:
                await self.entity_log_manager.create(
                    obj=EntityLogCreateSchema(
                        entity_type=EntityTypeEnum.SALE,
                        old_value=serialize_for_json(old_sale.to_dict()),
                        new_value=serialize_for_json(sale.to_dict()),
                    )
                )
                log.info("Updated data", sale=sale.to_dict(), old_sale=old_sale.to_dict())
