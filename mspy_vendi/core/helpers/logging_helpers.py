from typing import TYPE_CHECKING, Any

from fastapi import Request
from fastapi.websockets import WebSocket

if TYPE_CHECKING:
    from mspy_vendi.domain.user.models import User


def get_described_user_info(
    user: "User", /, request: Request | None = None, websocket: WebSocket | None = None
) -> dict[str, Any]:
    """
    Returns described user info.

    :param request: FastAPI request.
    :param websocket: FastAPI WebSocket.
    :param user: The user object.

    :return: Described user info.
    """
    connection: Request | WebSocket = request or websocket

    return {
        "user_id": user.id,
        "user_email": user.email,
        "user_firstname": user.firstname,
        "user_lastname": user.lastname,
        "user_is_active": user.is_active,
        "user_is_superuser": user.is_superuser,
        "user_is_verified": user.is_verified,
        "user_created_at": user.created_at.isoformat(),
        "url": connection.url.path if request else None,
        "method": connection.method if isinstance(connection, Request) else "websocket",
        "connection_type": "request" if request else "websocket",
    }
