import json
import re
from datetime import datetime

from sqlalchemy import Join, Select, Table
from sqlalchemy.orm import DeclarativeBase


def pascal_to_snake(pascal_string: str) -> str:
    # Regular expression to find capital letters preceded by a lowercase letter
    pattern = r"(?<!^)(?=[A-Z])"

    return re.sub(pattern, "_", pascal_string).lower()


def is_join_present(select_statement: Select, join_table: type[DeclarativeBase]) -> bool:
    """
    Checks if a join involving a specific table is present in a given SQL select statement.

    This function inspects the 'JOIN' components of a 'Select' object from SQLAlchemy’s SQL expression language.
    It evaluates whether any of the 'JOIN' components includes the specified table.

    :param: select_statement (Select): The SQLAlchemy Select object to be inspected.

    :param: join_table (Type[DeclarativeMeta]): A class that inherits from SQLAlchemy’s DeclarativeBase

    :return: True if the specified table is part of a join in the select statement’s 'from' components;
        otherwise, returns False.
    """

    def find_tables_in_join(join_attribute: Join) -> list[Table | DeclarativeBase]:
        """
        Reveal the nested JOIN stmts and recursively iterate through provided `join_attribute` to correctly assemble
        the final tables which occurred in statement.

        :param: join_attribute (Join): Instance of Join class, which consists of left and right part to determine the
        tables, which we include in JOIN clause.
        """
        left_part: list[DeclarativeBase] = []
        right_part: list[DeclarativeBase] = []

        if isinstance(join_attribute.left, Join):
            left_part = find_tables_in_join(join_attribute.left)

        if isinstance(join_attribute.right, Join):
            right_part = find_tables_in_join(join_attribute.right)

        return [*(left_part or [join_attribute.left]), *(right_part or [join_attribute.right])]

    for join_element in select_statement.get_final_froms():
        if isinstance(join_element, Join):
            if join_table.__table__ in [
                *(
                    find_tables_in_join(join_element.left)
                    if isinstance(join_element.left, Join)
                    else [join_element.left]
                ),
                *(
                    find_tables_in_join(join_element.right)
                    if isinstance(join_element.right, Join)
                    else [join_element.right]
                ),
            ]:
                return True

    return False


def get_columns_for_model(model: type[DeclarativeBase]) -> list[str]:
    """
    Retrieve the column names for a SQLAlchemy model.

    This function extracts the column names from the SQLAlchemy model class.

    :param: model (type[DeclarativeBase]): The SQLAlchemy model class from which to extract column names.

    :return: A list of column names for the specified model.
    """
    return model.__table__.columns.keys()


def serialize_for_json(data: dict) -> dict:
    def default_converter(o):
        if isinstance(o, datetime):
            return o.isoformat()
        return str(o)

    return json.loads(json.dumps(data, default=default_converter))
