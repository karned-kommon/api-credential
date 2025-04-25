import logging
import hvac
from hvac.exceptions import InvalidPath
from fastapi import HTTPException
from typing import Dict

from config.config import VAULT_HOST, VAULT_PORT, VAULT_TOKEN, VAULT_SECRET_PATH

client = hvac.Client(url=f"{VAULT_HOST}:{VAULT_PORT}", token=VAULT_TOKEN)

def get_secret(entity_uuid: str, licence_uuid: str, service: str) -> Dict[str, str]:
    logging.info(f"Getting secret for entity {entity_uuid}, license {licence_uuid}, service {service}")
    path = f"entities/{entity_uuid}/licenses/{licence_uuid}/{service}"

    try:
        secret = client.secrets.kv.v2.read_secret_version(
            path=path, mount_point=VAULT_SECRET_PATH
        )
        return secret["data"]["data"]
    except InvalidPath:
        raise HTTPException(status_code=404, detail="Secret not found")
    except Exception as e:
        logging.error(f"Error retrieving secret: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def create_secret(entity_uuid: str, license_uuid: str, service: str, secret_data: Dict[str, str]) -> Dict[str, str]:
    logging.info(f"Creating secret for entity {entity_uuid}, license {license_uuid}, service {service}")
    path = f"entities/{entity_uuid}/licenses/{license_uuid}/{service}"

    try:
        client.secrets.kv.v2.create_or_update_secret(
            path=path,
            mount_point=VAULT_SECRET_PATH,
            secret=secret_data
        )
        return {"message": "Secret recorded successfully"}
    except Exception as e:
        logging.error(f"Error creating secret: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
