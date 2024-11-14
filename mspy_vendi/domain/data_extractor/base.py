from typing import Any, Generic, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

DataType = TypeVar("DataType", bound=Any)
ReturnType = TypeVar("ReturnType", bound=Any)


class BaseDataExtractorClient(Generic[DataType, ReturnType]):
    """
    Base class for data extractors.
    Has an abstract method extract that should be implemented in the child classes.

    :param session: SQLAlchemy AsyncSession instance.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def extract(self, data: DataType) -> ReturnType:
        raise NotImplementedError
