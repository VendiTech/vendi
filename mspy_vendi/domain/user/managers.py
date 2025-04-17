from typing import Any

from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import CTE, ColumnClause, Select, asc, desc, func, label, select, update
from sqlalchemy.orm import joinedload

from mspy_vendi.core.exceptions.base_exception import BadRequestError, NotFoundError
from mspy_vendi.core.manager import CRUDManager, UpdateSchema
from mspy_vendi.core.pagination import Page
from mspy_vendi.domain.machines.models import Machine, MachineUser
from mspy_vendi.domain.product_user.models import ProductUser
from mspy_vendi.domain.products.models import Product
from mspy_vendi.domain.user.enums import PermissionEnum
from mspy_vendi.domain.user.filters import UserFilter
from mspy_vendi.domain.user.models import User
from mspy_vendi.domain.user.schemas import UserAllSchema, UserCompanyLogoImageSchema


class UserManager(CRUDManager):
    sql_model = User

    async def update_permissions(self, modified_user: User, permissions: list[PermissionEnum]) -> User:
        """
        Update the permissions of the user.
        Check if the permissions are already present in the user's permissions.
        And merge the permissions with the user's permissions.

        :param modified_user: The user to update.
        :param permissions: The permissions to update.

        :return: The updated user.
        """
        updated_permissions: set[PermissionEnum] = set(modified_user.permissions) | set(permissions)

        modified_user.permissions = list(updated_permissions)
        await self.session.commit()
        await self.session.refresh(modified_user)

        return modified_user

    async def delete_permissions(self, modified_user: User, permissions: list[PermissionEnum]) -> User:
        """
        Delete the permissions of the user.
        Check if the permissions are already present in the user's permissions.
        And subtract the permissions with the user's permissions.

        :param modified_user: The user to update.
        :param permissions: The permissions to update.

        :return: The updated user.
        """
        updated_permissions: set[PermissionEnum] = set(modified_user.permissions) - set(permissions)

        modified_user.permissions = list(updated_permissions)
        await self.session.commit()
        await self.session.refresh(modified_user)

        return modified_user

    async def update(
        self,
        obj_id: int,
        obj: UpdateSchema,
        autocommit: bool = True,
        is_unique: bool = False,
        raise_error: bool = True,
        **_: Any,
    ) -> User:
        """
        Updates an object.

        :param obj: The object to update.
        :param obj_id: The ID of the object to update.
        :param autocommit: If True, commit changes immediately, otherwise flush changes.
        :param is_unique: If True, apply unique filtering to the objects, otherwise do nothing.
        :param raise_error: If True, raise an error if the object is not found, otherwise return None.
        :param kwargs: Additional keyword arguments.

        :returns: The updated object.
        """
        if (
            not (updated_model := obj.model_dump(exclude_defaults=True, exclude={"machines", "products"}))
            and raise_error
        ):
            raise BadRequestError("No data provided for updating")

        stmt = (
            update(self.sql_model).where(self.sql_model.id == obj_id).values(**updated_model).returning(self.sql_model)
        )

        return await self._apply_changes(stmt=stmt, obj_id=obj_id, autocommit=autocommit, is_unique=is_unique)

    async def get_users_images(self) -> Page[UserCompanyLogoImageSchema]:
        """
        Helper method for Admin user to receive company-logo images for all users

        :return: Paginated list of company-logo images.
        """
        stmt_user_id = label("user_id", self.sql_model.id)
        stmt_user_company_logo_image = label("company_logo_image", self.sql_model.company_logo_image)

        stmt = select(stmt_user_id, stmt_user_company_logo_image)

        return await paginate(self.session, stmt)

    async def get(self, obj_id: int, *, raise_error: bool = True, **_: Any) -> User | None:
        """
        Get a user by ID.

        :param obj_id: The ID of the user to retrieve.
        :param raise_error: If True, raise an error if the user is not found, otherwise return None.

        :return: The user object if found, otherwise None.
        """
        stmt = (
            self.get_query()
            .where(self.sql_model.id == obj_id)
            .options(joinedload(self.sql_model.machine_users).joinedload(MachineUser.machine))
            .options(joinedload(self.sql_model.product_users).joinedload(ProductUser.product))
        )

        if not (result := await self.session.scalar(stmt)) and raise_error:
            raise NotFoundError(detail=f"{self.sql_model.__name__} object with {obj_id=} not found")

        return result

    @staticmethod
    def build_machine_counts_cte(query_filter: UserFilter) -> CTE:
        """
        Build a CTE for counting machines per user, with optional machine_id and geography filters.

        :param query_filter: The filter to apply to the query.

        :return: The CTE for counting machines per user.
        """
        cte = (
            select(MachineUser.user_id, label("machine_count", func.count(MachineUser.id)))
            .select_from(MachineUser)
            .group_by(MachineUser.user_id)
        )

        filters = []

        if query_filter.machine_id__in:
            filters.append(MachineUser.machine_id.in_(query_filter.machine_id__in))
            setattr(query_filter, "machine_id__in", None)

        if query_filter.geography_id__in:
            cte = cte.join(Machine, Machine.id == MachineUser.machine_id)

            filters.append(Machine.geography_id.in_(query_filter.geography_id__in))
            setattr(query_filter, "geography_id__in", None)

        if filters:
            cte = cte.where(*filters)

        return cte.cte("machine_counts_cte")

    @staticmethod
    def build_product_counts_cte(query_filter: UserFilter) -> CTE:
        """
        Build a CTE for counting products per user, with optional product filters.

        :param query_filter: The filter to apply to the query.

        :return: The CTE for counting products per user.
        """
        cte = (
            select(ProductUser.user_id, label("product_count", func.count(ProductUser.id)))
            .select_from(ProductUser)
            .group_by(ProductUser.user_id)
        )

        filters = []

        if query_filter.product_id__in:
            filters.append(ProductUser.product_id.in_(query_filter.product_id__in))
            setattr(query_filter, "product_id__in", None)

        if query_filter.product_category_id__in:
            cte = cte.join(Product, Product.id == ProductUser.product_id)

            filters.append(Product.product_category_id.in_(query_filter.product_category_id__in))
            setattr(query_filter, "product_category_id__in", None)

        if filters:
            cte = cte.where(*filters)

        return cte.cte("product_counts_cte")

    @staticmethod
    def sort_additional_fields(
        column_mapping: dict[str, ColumnClause],
        query_filter: UserFilter,
        stmt: Select,
    ) -> Select:
        """
        Sort additional fields based on the order_by parameter in the query filter.

        :param column_mapping: The mapping of field names to their corresponding SQLAlchemy columns.
        :param query_filter: The filter to apply to the query.
        :param stmt: The SQLAlchemy statement to modify.

        :return: The modified SQLAlchemy statement.
        """
        for field_name_with_direction in query_filter.order_by:
            field_name: str = field_name_with_direction.replace("-", "").replace("+", "")

            if field_name not in query_filter.Constants.extra_order_by_fields:
                continue

            if field_name_with_direction.startswith("-"):
                stmt = stmt.order_by(desc(column_mapping[field_name]).nullslast())
            else:
                stmt = stmt.order_by(asc(column_mapping[field_name]).nullsfirst())

            # Remove the field from the `order_by` list.
            query_filter.order_by.remove(field_name_with_direction)

        return stmt

    async def get_all(
        self,
        query_filter: UserFilter | None = None,
        raw_result: bool = False,
        is_unique: bool = False,
        **_: Any,
    ) -> Page[UserAllSchema] | list[User]:
        """
        Get all users.

        :param query_filter: The filter to apply to the query.
        :param raw_result: If True, return the raw result, otherwise return the mapped result.
        :param is_unique: If True, apply unique filtering to the objects, otherwise do nothing.

        :return: A list of users.
        """
        number_of_machines_field: str = "number_of_machines"
        number_of_products_field: str = "number_of_products"
        machine_counts_cte: CTE = self.build_machine_counts_cte(query_filter)
        product_counts_cte: CTE = self.build_product_counts_cte(query_filter)

        stmt = (
            select(
                func.json_build_object(
                    "id",
                    self.sql_model.id,
                    "firstname",
                    self.sql_model.firstname,
                    "lastname",
                    self.sql_model.lastname,
                    "email",
                    self.sql_model.email,
                    "company_name",
                    self.sql_model.company_name,
                    "job_title",
                    self.sql_model.job_title,
                    "phone_number",
                    self.sql_model.phone_number,
                    "status",
                    self.sql_model.status,
                    "role",
                    self.sql_model.role,
                    "permissions",
                    self.sql_model.permissions,
                    "is_verified",
                    self.sql_model.is_verified,
                    "last_logged_in",
                    self.sql_model.last_logged_in,
                    number_of_machines_field,
                    func.coalesce(machine_counts_cte.c.machine_count, 0),
                    number_of_products_field,
                    func.coalesce(product_counts_cte.c.product_count, 0),
                )
            )
            .outerjoin(machine_counts_cte, machine_counts_cte.c.user_id == self.sql_model.id)
            .outerjoin(product_counts_cte, product_counts_cte.c.user_id == self.sql_model.id)
        )

        stmt = query_filter.filter(stmt)

        column_mapping = {
            number_of_machines_field: machine_counts_cte.c.machine_count,
            number_of_products_field: product_counts_cte.c.product_count,
        }
        stmt = self.sort_additional_fields(column_mapping, query_filter, stmt)

        stmt = query_filter.sort(stmt)

        if raw_result:
            if is_unique:
                return (await self.session.execute(stmt)).unique().all()  # type: ignore

            return (await self.session.scalars(stmt)).all()  # type: ignore

        return await paginate(self.session, stmt, unique=is_unique)
