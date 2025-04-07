from datetime import date, datetime, timedelta
from typing import Any, cast

from fastapi import Query as QueryParameter
from fastapi_filter.contrib.sqlalchemy import Filter
from fastapi_filter.contrib.sqlalchemy.filter import _orm_operator_transformer
from pydantic import Field, field_validator, model_validator
from sqlalchemy import BinaryExpression, Column, Select, func, or_
from sqlalchemy.orm import DeclarativeBase, Query

from mspy_vendi.core.constants import COMPOUND_SEARCH_FIELD_NAME
from mspy_vendi.core.helpers import get_columns_for_model, is_join_present, set_end_of_day_time


class BaseFilter(Filter, extra="allow"):  # type: ignore
    """
    Base filter for ORM related filters.
    This filter extends the base filter from fastapi_filter.contrib.sqlalchemy.
    It adds a validator to restrict the sortable fields.
    This is useful to prevent the user from sorting by fields that are not sortable.

    All children must set this, if they want to allow only certain fields to be sortable:
        ```python
        class Constants(BaseFilter.Constants):
            allowed_order_by_fields = ["field1", "field2"]
        ```

    All children must set this, if they want to disallow certain fields to be sortable:
        ```python
        class Constants(BaseFilter.Constants):
            disallowed_order_by_fields = ["field1", "field2"]
        ```
    """

    class Constants(Filter.Constants):
        fields_for_insensitive_search: list[str] | None = None
        allowed_order_by_fields: list[str] | None = None
        disallowed_order_by_fields: list[str] | None = None
        multi_search_fields: list[str] | None = None
        date_range_fields: list[str] | None = None
        default_date_range_db_field: str = "created_at"
        age_range_fields: list[str] | None = None

    @model_validator(mode="before")
    def check_date_range_fields(cls, values: dict) -> dict:
        if not (date_range_fields := getattr(cls.Constants, "date_range_fields", [])):
            return values

        db_model: type[DeclarativeBase] = cast(type[DeclarativeBase], cls.Constants.model)

        if cls.Constants.default_date_range_db_field not in get_columns_for_model(db_model):
            raise ValueError(
                "You can't use date range fields without the corresponding "
                f"`{cls.Constants.default_date_range_db_field}` in DB table."
            )

        for field in date_range_fields:
            if field not in cls.model_fields:
                raise ValueError(
                    f"The field '{field}' specified in 'Constant.date_range_fields' "
                    "must be present in 'FilterModel' fields."
                )

        date_from_field, date_to_field = date_range_fields

        if (values.get(date_from_field) or datetime.min) > (values.get(date_to_field) or datetime.max):
            raise ValueError(f"`{date_from_field}` can't be less than `{date_to_field}`")

        return values

    @model_validator(mode="before")
    def check_multi_search_fields_existence(cls, values: dict) -> dict:
        multi_search_fields: list[str] = getattr(cls.Constants, "multi_search_fields", []) or []

        if not multi_search_fields and COMPOUND_SEARCH_FIELD_NAME not in cls.model_fields:
            return values

        if not multi_search_fields and COMPOUND_SEARCH_FIELD_NAME in cls.model_fields:
            raise ValueError(
                f"Field '{COMPOUND_SEARCH_FIELD_NAME}' must not be present in the model fields "
                "without the `multi_search_fields` Constant."
            )

        if multi_search_fields and COMPOUND_SEARCH_FIELD_NAME not in cls.model_fields:
            raise ValueError(
                f"Field '{COMPOUND_SEARCH_FIELD_NAME}' must be present in the model fields to use multi search."
            )

        db_model: type[DeclarativeBase] = cast(type[DeclarativeBase], cls.Constants.model)

        for field in multi_search_fields:
            if field not in get_columns_for_model(db_model):
                raise ValueError("You can't use values which are not presented in DB Model!")

        return values

    @model_validator(mode="before")
    def check_allowed_and_disallowed(cls, values: dict) -> dict:
        allowed = values.get("allowed_order_by_fields", [])
        disallowed = values.get("disallowed_order_by_fields", [])

        if allowed and disallowed:
            raise ValueError(
                "You cannot use both 'allowed_order_by_fields' and 'disallowed_order_by_fields' at the same time."
            )

        return values

    @model_validator(mode="before")
    def add_fields_to_search(cls, values: dict) -> dict:
        fields_to_search: set[str] = set(getattr(cls.Constants, "fields_for_insensitive_search", []) or set())

        for value in fields_to_search:
            if value not in cls.model_fields:
                raise ValueError(
                    "You can't use values which are not presented in FilterModel "
                    "fields in `fields_for_insensitive_search`"
                )

            if not values.get(f"{value}__ilike"):
                values[f"{value}__ilike"] = values.pop(value, None)

        return values

    @model_validator(mode="before")
    def trim_the_order_by(cls, values: dict) -> dict:
        """
        Since version `1.0.0` of fastapi_filter, there is a known issue when using a plus sign (+)
        as the first character in a filter.

        The library incorrectly replaces the initial + with an empty string ("").
        To address this issue, we manually trim the validated value to remove any leading space
        and ensure the `+` sign is correctly included in the filter.

        This workaround corrects the unintended behavior of the library.
        """
        if (order_by_field := values.get("order_by")) and isinstance(order_by_field, str):
            values["order_by"] = order_by_field.strip()

        return values

    @field_validator("order_by", check_fields=False)
    def restrict_sortable_fields(cls, field_names: list[str] | None):
        if field_names is None:
            return None

        allowed = set(getattr(cls.Constants, "allowed_order_by_fields", []) or [])
        disallowed = set(getattr(cls.Constants, "disallowed_order_by_fields", []) or [])

        cleaned_field_names = {name.replace("+", "").replace("-", "") for name in field_names}

        not_allowed_fields = cleaned_field_names - allowed if allowed else set()
        disallowed_fields = cleaned_field_names.intersection(disallowed)

        if not_allowed_fields:
            raise ValueError(f"You may only sort by: {', '.join(allowed)}")

        if disallowed_fields:
            raise ValueError(f"You may not sort by: {', '.join(disallowed)}")

        return field_names

    def filter(self, query: Query | Select, autojoin: bool = True):
        """
        NOTE: The most part of the code is copied from the original implementation.
        The difference is as follows:
            - implementation of date range filter.
            - implementation of nested filter logic.
            - ability to filter by date (if `datetime` annotation).
            - implementation of compound search logic.

        That's why, be careful when updating current implementation.

        :param query: Query object or actual SQL query.
        :param autojoin: Flag which specifies if we need to do implicit join, pass False if you have a complex query
                         with joins on your side.

        :return: Implicitly modified query object which we executed in the caller function.
        """
        if (range_fields := self.Constants.date_range_fields) and self.filtering_fields:
            date_from_field, date_to_field = range_fields

            date_from: datetime = getattr(self, date_from_field) or datetime.min
            date_to: datetime = set_end_of_day_time(getattr(self, date_to_field) or datetime.max)

            query: Select = query.where(
                getattr(self.Constants.model, self.Constants.default_date_range_db_field).between(date_from, date_to)
            )

        # We get rid of range fields, because we've been already construct the query above
        filtering_fields_without_range_fields: list[tuple[str, Any]] = [
            (key, value) for key, value in self.filtering_fields if key not in (range_fields or [])
        ]

        for field_name, value in filtering_fields_without_range_fields:
            field_value: BaseFilter | str = getattr(self, field_name)

            if isinstance(field_value, BaseFilter):
                # If the field is a nested filter, we need to join the model and apply the filter.
                # In original implementation, `fastapi-filter` utilized the cartesian product of the tables, i.e.
                # >>> FROM root_table, nested_table
                # That's why previous realisation returns irrelevant final results.
                if autojoin and not is_join_present(query, field_value.Constants.model):  # type: ignore
                    query: Select = query.join(field_value.Constants.model)

                query: Select = field_value.filter(query, autojoin=autojoin)

            elif field_name == COMPOUND_SEARCH_FIELD_NAME:
                # If the field is a compound search field, we need to apply the filter to all the fields.
                search_filters: list[BinaryExpression] = [
                    getattr(self.Constants.model, field).ilike(f"%{value}%")
                    for field in self.Constants.multi_search_fields or []
                ]

                query: Select = query.filter(or_(*search_filters))

            elif isinstance(field_value, date):
                # In order to filter by date we need to cast the `datetime` field into date.
                query: Select = query.filter(func.date(getattr(self.Constants.model, field_name)) == field_value)

            else:
                if "__" in field_name:
                    field_name, operator = field_name.split("__")
                    operator, value = _orm_operator_transformer[operator](value)
                else:
                    operator: str = "__eq__"

                if field_name == self.Constants.search_field_name and hasattr(self.Constants, "search_model_fields"):
                    search_filters: list[BinaryExpression] = [
                        getattr(self.Constants.model, field).ilike(f"%{value}%")
                        for field in self.Constants.search_model_fields
                    ]
                    query: Select = query.filter(or_(*search_filters))
                else:
                    model_field: Column = getattr(self.Constants.model, field_name)
                    query: Select = query.filter(getattr(model_field, operator)(value))

        return query

    def group_by(self, query: Query | Select) -> Query | Select:
        """
        Group by the query by the fields provided in the `order_by` attribute.
        """
        if not self.ordering_values:
            return query

        for field_name in self.ordering_values:
            field_name = field_name.replace("-", "").replace("+", "")

            group_by_field = getattr(self.Constants.model, field_name)

            query = query.group_by(group_by_field)

        return query

    def set_without_validation(self, name: str, value: Any) -> None:
        """
        Workaround to be able to set fields without validation.

        Because due to the validate_assignment=True, we can't set fields without validation.
        And as fact, it raises the RecursionError.
        """
        attr = getattr(self.__class__, name, None)

        if isinstance(attr, property):
            attr.__set__(self, value)
        else:
            self.__dict__[name] = value
            self.__pydantic_fields_set__.add(name)


class DateRangeFilter(BaseFilter):
    """
    Child class of the BaseFilter for proper validation of the date_range_fields attribute.
    """

    date_from: datetime | None = Field(QueryParameter(None, description="Default value: `current date - 30 days`"))
    date_to: datetime | None = None

    @model_validator(mode="after")
    def validate_date_params(self):
        """
        Check current date range parameters and set default values if they are not set.
        Example:
            - if date_from is not set, it will be set to 30 days ago.
            - if date_to is not set, it will be set to the current date.

        :return: self
        """
        current_datetime = datetime.now()

        if not self.date_from:
            self.set_without_validation("date_from", current_datetime - timedelta(days=30))

        if not self.date_to:
            self.set_without_validation("date_to", current_datetime)

        return self
