from fastapi_users.authentication import AuthenticationBackend, CookieTransport, JWTStrategy

from mspy_vendi.config import config

cookie_transport = CookieTransport(
    cookie_name=config.auth_cookie_name,
    cookie_max_age=config.token_lifetime,
    cookie_samesite="none",
    cookie_secure=config.auth_cookie_secure,
)


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=config.secret_key, lifetime_seconds=config.token_lifetime)


backend = AuthenticationBackend(name="jwt", transport=cookie_transport, get_strategy=get_jwt_strategy)
