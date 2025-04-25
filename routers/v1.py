from typing import Dict
import hvac
from hvac.exceptions import InvalidPath

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from config.config import API_TAG_NAME, VAULT_HOST, VAULT_PORT, VAULT_TOKEN, VAULT_SECRET_PATH

VERSION = "v1"
api_group_name = f"/{API_TAG_NAME}/{VERSION}/"

class SecretRequest(BaseModel):
    data: Dict[str, str]

client = hvac.Client(url=f"{VAULT_HOST}:{VAULT_PORT}", token=VAULT_TOKEN)


router = APIRouter(
    tags=[api_group_name],
    prefix=f"/credential/{VERSION}"
)



@router.get("/{service}")
def get_secret(request: Request, service: str):
    entity_uuid = request.state.entity_uuid
    licence_uuid = request.state.licence_uuid
    path = f"entities/{entity_uuid}/licenses/{licence_uuid}/{service}"

    try:
        secret = client.secrets.kv.v2.read_secret_version(
            path=path, mount_point=VAULT_SECRET_PATH
        )
        return secret["data"]["data"]
    except hvac.exceptions.InvalidPath:
        raise HTTPException(status_code=404, detail="Secret not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{license_uuid}/{service}")
def create_secret(
    request: Request, license_uuid: str, service: str, secret_request: Dict[str, str]
):
    entity_uuid = request.state.entity_uuid
    path = f"entities/{entity_uuid}/licenses/{license_uuid}/{service}"

    try:
        client.secrets.kv.v2.create_or_update_secret(
            path=path,
            mount_point=VAULT_SECRET_PATH,
            secret=secret_request
        )
        return {"message": "Secret recorded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

