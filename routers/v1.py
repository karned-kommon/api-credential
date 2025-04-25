from typing import Dict

from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel

from config.config import API_TAG_NAME
from services.items_service import get_secret, create_secret

VERSION = "v1"
api_group_name = f"/{API_TAG_NAME}/{VERSION}/"

class SecretRequest(BaseModel):
    data: Dict[str, str]

router = APIRouter(
    tags=[api_group_name],
    prefix=f"/credential/{VERSION}"
)

@router.get("/{service}")
async def read_secret(request: Request, service: str):
    entity_uuid = request.state.entity_uuid
    licence_uuid = request.state.licence_uuid

    return get_secret(entity_uuid, licence_uuid, service)

@router.post("/{license_uuid}/{service}")
async def create_new_secret(
    request: Request, 
    license_uuid: str, 
    service: str, 
    secret_request: Dict[str, str]
):
    entity_uuid = request.state.entity_uuid

    return create_secret(entity_uuid, license_uuid, service, secret_request)
