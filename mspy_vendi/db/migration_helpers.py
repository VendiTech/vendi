from alembic import op
from sqlalchemy import text


def table_has_column(table: str, column: str) -> bool:
    conn = op.get_bind()
    query_string = f"""
    SELECT EXISTS(
        SELECT 1 FROM information_schema.columns
        WHERE table_name = '{table}' AND column_name = '{column}'
    )
    """
    result = conn.execute(text(query_string))

    return result.scalar_one()


def table_exists(table: str) -> bool:
    conn = op.get_bind()
    query_string = f"""
    SELECT EXISTS(
        SELECT 1 FROM information_schema.tables
        WHERE table_name = '{table}'
    )
    """
    result = conn.execute(text(query_string))

    return result.scalar_one()


def index_exists(name: str) -> bool:
    conn = op.get_bind()
    query_string = f"SELECT EXISTS(SELECT 1 FROM pg_indexes WHERE indexname = '{name}') AS idx_exists;"
    result = conn.execute(text(query_string))

    return result.scalar_one()


def enum_exists(enum_name: str) -> bool:
    conn = op.get_bind()
    query_string = f"SELECT count(*) FROM pg_type WHERE typcategory = 'E' and typname = '{enum_name}';"
    result = conn.execute(text(query_string))

    return result.scalar_one()


def enum_has_value(enum_name: str, enum_value: str) -> bool:
    conn = op.get_bind()
    query_string = f"""
        SELECT EXISTS(
            SELECT 1 FROM pg_type t JOIN pg_enum e ON e.enumtypid = t.oid
            WHERE t.typtype = 'e' AND t.typname = '{enum_name}' AND e.enumlabel = '{enum_value}'
        );
    """
    result = conn.execute(text(query_string))
    return result.scalar_one()


def constraint_exists(constraint_name: str) -> bool:
    conn = op.get_bind()
    query_string = f"SELECT EXISTS(SELECT 1 FROM pg_constraint WHERE conname = '{constraint_name}');"
    result = conn.execute(text(query_string))
    return result.scalar_one()


def extension_exist(extension_name) -> bool:
    conn = op.get_bind()
    query_string = f"""SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = '{extension_name}');"""
    result = conn.execute(text(query_string))
    return result.scalar_one()
