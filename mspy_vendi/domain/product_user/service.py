from mspy_vendi.core.service import CRUDService
from mspy_vendi.domain.product_user.manager import ProductUserManager


class ProductUserService(CRUDService):
    manager_class = ProductUserManager

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
