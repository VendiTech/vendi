from sqlalchemy.ext.asyncio import AsyncSession

from mspy_vendi.config import log
from mspy_vendi.domain.geographies.manager import GeographyManager
from mspy_vendi.domain.geographies.schemas import GeographyCreateSchema
from mspy_vendi.domain.machines.manager import MachineManager
from mspy_vendi.domain.machines.schemas import MachineCreateSchema
from mspy_vendi.domain.nayax.schemas import NayaxTransactionSchema
from mspy_vendi.domain.product_category.manager import ProductCategoryManager
from mspy_vendi.domain.product_category.schemas import CreateProductCategorySchema
from mspy_vendi.domain.products.manager import ProductManager
from mspy_vendi.domain.products.schemas import CreateProductSchema
from mspy_vendi.domain.sales.manager import SaleManager
from mspy_vendi.domain.sales.schemas import SaleCreateSchema


class NayaxService:
    def __init__(self, db_session: AsyncSession):
        self.geography_manager = GeographyManager(db_session)
        self.machine_manager = MachineManager(db_session)
        self.product_manager = ProductManager(db_session)
        self.product_category_manager = ProductCategoryManager(db_session)
        self.sale_manager = SaleManager(db_session)

    async def process_message(self, message: NayaxTransactionSchema) -> None:
        geography, is_created = await self.geography_manager.get_or_create(
            name=message.data.area_description or message.data.actor_description,
            obj=GeographyCreateSchema(
                name=message.data.area_description or message.data.actor_description,
                postcode=str(message.data.location_code or message.data.actor_code),
            ),
        )

        log.info("Geography object", geography_name=geography.name, is_created=is_created)

        machine, is_created = await self.machine_manager.get_or_create(
            obj_id=message.machine_id,
            obj=MachineCreateSchema(
                name=message.data.machine_name,
                geography_id=geography.id,
            ),
        )

        log.info("Machine object", machine_id=machine.id, is_created=is_created)

        for product_item in message.data.products:
            log.info("Start working with the following product", product_id=product_item.product_id)

            product_category, is_created = await self.product_category_manager.get_or_create(
                name=product_item.product_group,
                obj=CreateProductCategorySchema(name=product_item.product_group),
            )

            log.info(
                "Product category object",
                product_category_name=product_category.name,
                is_created=is_created,
            )

            log.info(
                "Provided Product object",
                product_id=product_item.product_id,
                price=product_item.product_bruto,
            )

            product, is_created = await self.product_manager.get_or_create(
                obj_id=product_item.product_id,
                obj=CreateProductSchema(
                    name=product_item.product_name,
                    price=product_item.product_bruto,
                    product_category_id=product_category.id,
                ),
            )

            log.info("Product object", product_id=product.id, is_created=is_created)

            log.info(
                "Provided Sale object",
                sale_id=message.transaction_id,
                quantity=product_item.product_quantity,
                source_system_id=message.transaction_id,
            )
            sale_datetime = message.machine_time or message.data.machine_au_time
            sale, is_created = await self.sale_manager.get_or_create(
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

            log.info("Sale object", sale_id=sale.id, is_created=is_created)
