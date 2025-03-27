from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import DBAPIError

from mspy_vendi.core.exceptions.base_exception import raise_db_error
from mspy_vendi.core.manager import CRUDManager
from mspy_vendi.domain.product_user.models import ProductUser


class ProductUserManager(CRUDManager):
    """
    Manages the association between users and products in the database.

    This class provides methods to attach products to a user, disassociate products from a user,
    and retrieve the list of product IDs associated with a specific user.
    """
    sql_model = ProductUser

    async def attach_user_to_product(self, user_id: int, *product_ids: int) -> None:
        """
        Associates a user with one or more products by inserting records into the database.

        :param user_id: The ID of the user to associate with products.
        :param product_ids: One or more product IDs to associate with the user.

        :raise DBAPIError: Raised if the database encountered an error.
        """
        try:
            await self.session.execute(
                insert(self.sql_model),
                [dict(user_id=user_id, product_id=product_id) for product_id in set(product_ids)],
            )
            await self.session.commit()

        except DBAPIError as ex:
            await self.session.rollback()
            raise_db_error(ex)

    async def disassociate_user_with_product(self, user_id: int, *product_ids: int) -> None:
        """
        Disassociates a user from one or more products by deleting corresponding records.

        :param user_id: The ID of the user to disassociate.
        :param product_ids: One or more product IDs to disassociate.

        :raise DBAPIError: Raised if the database encountered an error.
        """
        try:
            await self.session.execute(
                delete(self.sql_model).where(
                    self.sql_model.user_id == user_id, self.sql_model.product_id.in_(product_ids)
                ),
            )
            await self.session.commit()

        except DBAPIError as ex:
            await self.session.rollback()
            raise_db_error(ex)

    async def get_products_for_user(self, user_id: int) -> list[int]:
        """
        Retrieves a list of product IDs associated with a given user.

        :param user_id: The ID of the user whose associated products are to be retrieved.
        :return: A list of product IDs associated with the user.
        """
        stmt = select(self.sql_model.product_id).where(self.sql_model.user_id == user_id)

        return (await self.session.scalars(stmt)).all()  # type: ignore
