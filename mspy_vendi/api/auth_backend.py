from fastapi_users.authentication import AuthenticationBackend, BearerTransport, JWTStrategy

from mspy_vendi.config import config

bearer_transport = BearerTransport(tokenUrl=config.login_url)


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=config.secret_key, lifetime_seconds=config.token_lifetime)


backend = AuthenticationBackend(name="jwt", transport=bearer_transport, get_strategy=get_jwt_strategy)
