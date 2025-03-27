from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse

from mspy_vendi.core.api import CRUDApi, admin_permissions, basic_endpoints
from mspy_vendi.core.enums import ApiTagEnum
from mspy_vendi.core.pagination import Page
from mspy_vendi.deps import get_db_session
from mspy_vendi.domain.products.schemas import ProductCreateSchema, ProductDetailSchema
from mspy_vendi.domain.products.service import ProductService

router = APIRouter(prefix="/products", default_response_class=ORJSONResponse, tags=[ApiTagEnum.PRODUCTS])


class ProductAPI(CRUDApi):
    service = ProductService
    schema = ProductDetailSchema
    create_schema = ProductCreateSchema
    current_user_mapping = admin_permissions
    endpoints = basic_endpoints
    get_db_session = Depends(get_db_session)
    pagination_schema = Page
    api_tags = (ApiTagEnum.PRODUCTS,)


ProductAPI(router)
