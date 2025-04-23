import os
import hvac
from hvac.exceptions import InvalidPath
from fastapi import HTTPException, FastAPI
from pydantic import BaseModel
from typing import Dict

import traceback

# Charge les infos depuis variables d'environnement
VAULT_URL = os.getenv("VAULT_ADDR", "http://localhost:57704")
VAULT_TOKEN = os.getenv("VAULT_TOKEN")
MOUNT_POINT = os.getenv("VAULT_MOUNT", "secret")

# Fixes (dans un vrai projet, mets-les ailleurs ou récupère dynamiquement)
ENTITY_UUID = os.getenv("ENTITY_UUID", "fake-entity-uuid")
LICENSE_UUID = os.getenv("LICENSE_UUID", "fake-license-uuid")

# Initialise le client Vault
client = hvac.Client(url=VAULT_URL, token=VAULT_TOKEN)

# FastAPI Router
app = FastAPI()

# Modèle Pydantic
class SecretRequest(BaseModel):
    service: str
    data: Dict[str, str]

# Crée un secret
@app.post("/secret")
def create_secret(secret_request: SecretRequest):
    """
    Create a secret in Vault under the given service name.
    """
    path = f"entities/{ENTITY_UUID}/licenses/{LICENSE_UUID}/{secret_request.service}"

    try:
        # Check si déjà existant
        existing = client.secrets.kv.v2.read_secret_version(
            path=path, mount_point=MOUNT_POINT
        )
        return {
            "message": "Secret already exists",
            "data": existing["data"]["data"]
        }
    except hvac.exceptions.InvalidPath:
        # Crée le secret
        client.secrets.kv.v2.create_or_update_secret(
            path=path,
            mount_point=MOUNT_POINT,
            secret=secret_request.data
        )
        return {"message": "Secret created successfully"}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# Récupère un secret
@app.get("/secret/{service}")
def get_secret(service: str):
    """
    Retrieve a secret from Vault by service name.
    """
    path = f"entities/{ENTITY_UUID}/licenses/{LICENSE_UUID}/{service}"

    try:
        secret = client.secrets.kv.v2.read_secret_version(
            path=path, mount_point=MOUNT_POINT
        )
        return {"data": secret["data"]["data"]}
    except hvac.exceptions.InvalidPath:
        raise HTTPException(status_code=404, detail="Secret not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))