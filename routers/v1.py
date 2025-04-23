from typing import Dict
import hvac
from hvac.exceptions import InvalidPath

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from config.config import API_TAG_NAME, VAULT_HOST, VAULT_PORT, VAULT_TOKEN, VAULT_SECRET_PATH

VERSION = "v1"
api_group_name = f"/{API_TAG_NAME}/{VERSION}/"

class SecretRequest(BaseModel):
    service: str
    data: Dict[str, str]

client = hvac.Client(url=f"{VAULT_HOST}:{VAULT_PORT}", token=VAULT_TOKEN)


router = APIRouter(
    tags=[api_group_name],
    prefix=f"/credential/{VERSION}"
)


@router.post("/secret")
def create_secret(request: Request, secret_request: SecretRequest):
    entity_uuid = request.state.entity_uuid
    license_uuid = request.state.license_uuid
    path = f"entities/{entity_uuid}/licenses/{license_uuid}/{secret_request.service}"

    try:
        existing = client.secrets.kv.v2.read_secret_version(
            path=path, mount_point=VAULT_SECRET_PATH
        )
        return {
            "message": "Secret already exists",
            "data": existing["data"]["data"]
        }
    except hvac.exceptions.InvalidPath:
        client.secrets.kv.v2.create_or_update_secret(
            path=path,
            mount_point=VAULT_SECRET_PATH,
            secret=secret_request.data
        )
        return {"message": "Secret created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/secret/{service}")
def get_secret(request: Request, service: str):
    entity_uuid = request.state.entity_uuid
    license_uuid = request.state.license_uuid
    path = f"entities/{entity_uuid}/licenses/{license_uuid}/{service}"

    try:
        secret = client.secrets.kv.v2.read_secret_version(
            path=path, mount_point=VAULT_SECRET_PATH
        )
        return {"data": secret["data"]["data"]}
    except hvac.exceptions.InvalidPath:
        raise HTTPException(status_code=404, detail="Secret not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))