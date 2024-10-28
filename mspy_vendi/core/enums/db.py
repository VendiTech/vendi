# mypy: ignore-errors
from enum import Enum, StrEnum


class PGErrorCodeEnum(StrEnum):
    """
    Enum for pg_code exception codes
    For more info, check the following link:
    https://github.com/MagicStack/asyncpg/blob/master/asyncpg/exceptions/__init__.py
    """

    FOREIGN_KEY_VIOLATION = "23503"
    NOT_NULL_VIOLATION = "23502"
    CONSTRAINT_VIOLATION = "23514"
    UNIQUE_VIOLATION = "23505"


class CascadesEnum(Enum):
    """
    PostgreSQL specific cascade types
    """

    CASCADE = "CASCADE"
    RESTRICT = "RESTRICT"
    NO_ACTION = "NO ACTION"
    SET_NULL = "SET NULL"
    SET_DEFAULT = "SET DEFAULT"


class ORMRelationshipCascadeTechniqueEnum(Enum):
    """
    Quick intro about this Enum.

    These are the parameters for the `relationship.passive_deletes` and for the `relationship.passive_updates`

    As you know, SQLAlchemy provides itself one more layer for handling the DELETE and UPDATE operation, hence
    via the cascade="...", you can provide several technique for cascade (the detail info you can find above).
    The problem here is that SQLAlchemy by default ignore the `CASCADES` which is defined in the DB layer.

    We noticed that with `ON DELETE RESTRICT` db constraint, and with relationship cascade we're able to delete the
    associated objects, despite DB constraints.

    Returning to the provided values, `passive_deletes` takes the following parameters:

    - False. Used as the default value. It’s important to note, that `relationship(cascade=...)` setting must be
    configured to achieve desired behavior (cascade="delete, {{ delete-orphan }} - optional"), in order to delete all
    related entities without requiring explicit actions.

    - True. A value of True indicates that unloaded child items should not be loaded during a delete operation
    on the parent. Marking this flag as True usually implies an ON DELETE <CASCADE|SET NULL> rule is in place which
    will handle updating/deleting child rows on the database side. Important to know if you provide
    the ForeignKey field as non-nullable, this technique will be still don't work. At first, SQLAlchemy tries to remove
    the parent model and update the child model with parent_id=null, but it throws an error, another conclusion that the
    technique doesn't build upon the `DB CASCADES`, so you need to utilize it carefully.

    - "all". Will disable the “nulling out” of the child foreign keys, when the parent object is deleted and there is
    no delete or delete-orphan cascade enabled. This is typically used when a triggering or error raise scenario is
    in place on the database side. So here, we rely on the database cascade checks.

    """

    true = True
    false = False
    all = "all"

    @classmethod
    @property
    def db_cascade(cls: "ORMRelationshipCascadeTechniqueEnum") -> str:
        return cls.all.value
