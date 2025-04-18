from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from mspy_vendi.core.service import CRUDService
from mspy_vendi.deps import get_db_session
from mspy_vendi.domain.product_user.manager import ProductUserManager
from mspy_vendi.domain.products.manager import ProductManager
from mspy_vendi.domain.user.managers import UserManager


class ProductUserService(CRUDService):
    manager_class = ProductUserManager

    def __init__(self, db_session: Annotated[AsyncSession, Depends(get_db_session)]):
        self.product_manager = ProductManager(db_session)
        self.user_manager = UserManager(db_session)
        super().__init__(db_session=db_session)

    async def update_user_products(self, user_id: int, *product_ids: int) -> None:
        """
        Update the products of the user.

        :param user_id: The user ID.
        :param product_ids: The product IDs.
        """
        current_products_set: set[int] = set(await self.manager.get_products_for_user(user_id=user_id))
        new_products_set: set[int] = set(product_ids)

        if products_to_add := new_products_set - current_products_set:
            await self.manager.attach_user_to_product(user_id, *products_to_add)

        if products_to_remove := current_products_set - new_products_set:
            await self.manager.disassociate_user_with_product(user_id, *products_to_remove)

    async def attach_all_products(self, user_id: int) -> None:
        """
        Attach all products to the user.

        :param user_id: The user ID.
        """
        # Check if the provided user_id exists
        await self.user_manager.get(user_id)

        current_products_set: set[int] = set(await self.manager.get_products_for_user(user_id=user_id))
        all_products_set: set[int] = set(await self.product_manager.get_all_product_ids())

        if products_to_add := all_products_set - current_products_set:
            await self.manager.attach_user_to_product(user_id, *products_to_add)
