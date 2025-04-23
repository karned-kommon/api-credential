import logging
import os
import time
from datetime import datetime, timezone
from typing import Any

import httpx
from fastapi import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from config.config import API_NAME, KEYCLOAK_HOST, KEYCLOAK_REALM, KEYCLOAK_CLIENT_ID, KEYCLOAK_CLIENT_SECRET, URL_API_GATEWAY
from decorators.log_time import log_time_async
from services.inmemory_service import get_redis_api_db
from utils.path_util import is_unprotected_path

r = get_redis_api_db()


def get_licences( token: str ) -> list:
    response = httpx.get(f"{URL_API_GATEWAY}/licence/v1/mine", headers={"Authorization": f"Bearer {token}"})
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Licences request failed")
    return response.json()

def filter_licences( licences: list) -> list:
    now = int(datetime.now(timezone.utc).timestamp())

    licences_filtered = [
        {
            "uuid": lic["uuid"],
            "type_uuid": lic["type_uuid"],
            "name": lic["name"],
            "iat": lic["iat"],
            "exp": lic["exp"],
            "entity_uuid": lic["entity_uuid"]
        }
        for lic in licences if lic["iat"] < now < lic["exp"]
    ]

    return licences_filtered

def generate_state_info( token_info: dict ) -> dict:
    return {
        "user_uuid": token_info.get("sub"),
        "user_display_name": token_info.get("preferred_username"),
        "user_email": token_info.get("email"),
        "user_audiences": token_info.get("aud"),
        "user_roles": token_info.get("resource_access").get(API_NAME).get("roles"),
        "cached_time": token_info.get("cached_time")
    }


def is_token_valid_audience( token_info: dict ) -> bool:
    aud = token_info.get("aud")
    return API_NAME in aud


def is_token_active( token_info: dict ) -> bool:
    now = int(time.time())
    iat = token_info.get("iat")
    exp = token_info.get("exp")

    if iat is not None and exp is not None:
        return iat < now < exp

    return False


def read_cache_token( token: str ) -> Any | None:
    cached_result = r.get(token)
    if cached_result is not None:
        return eval(cached_result)


def write_cache_token( token: str, cache_token: dict ):
    if cache_token.get("exp") is not None:
        ttl = cache_token.get("exp") - int(time.time())
        r.set(token, str(cache_token), ex=ttl)


def introspect_token( token: str ) -> dict:
    url = f"{KEYCLOAK_HOST}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/token/introspect"
    data = {
        "token": token,
        "client_id": KEYCLOAK_CLIENT_ID,
        "client_secret": KEYCLOAK_CLIENT_SECRET
    }

    response = httpx.post(url, data=data)
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Keycloak introspection failed")
    return response.json()


def prepare_cache_token( token: str, token_info: dict ) -> dict:
    cached_time = int(time.time())
    token_info["cached_time"] = cached_time
    licenses = get_licences(token)
    licenses_token = filter_licences(licenses)
    token_info["licenses"] = licenses_token
    return token_info


def get_token_info( token: str ) -> dict:
    response = read_cache_token(token)
    if not response:
        response = introspect_token(token)
        cache_token = prepare_cache_token(token, response)
        write_cache_token(token, cache_token)
    return response


def delete_cache_token( token: str ):
    r.delete(token)


def is_headers_token_present( request: Request ) -> bool:
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return False
    if not auth_header.startswith("Bearer "):
        return False
    return True


def extract_token( request: Request ) -> str:
    auth_header = request.headers.get("Authorization")
    token = auth_header.split(" ")[1]
    return token


def refresh_cache_token( request: Request ):
    check_headers_token(request)
    token = extract_token(request)
    delete_cache_token(token)
    token_info = get_token_info(token)
    check_token(token_info)
    state_token_info = generate_state_info(token_info)
    store_token_info_in_state(state_token_info, request)


def store_token_info_in_state( state_token_info: dict, request: Request ):
    request.state.token_info = state_token_info
    request.state.user_uuid = state_token_info.get("user_uuid")


def check_headers_token( request: Request ):
    if not is_headers_token_present(request):
        raise HTTPException(status_code=401, detail="Token manquant ou invalide")


def check_token( token_info ):
    if not is_token_active(token_info):
        raise HTTPException(status_code=401, detail="Token is not active")

    if not is_token_valid_audience(token_info):
        raise HTTPException(status_code=401, detail="Token is not valid for this audience")


class TokenVerificationMiddleware(BaseHTTPMiddleware):
    def __init__( self, app ):
        super().__init__(app)

    @log_time_async
    async def dispatch( self, request: Request, call_next ) -> Response:
        logging.info("TokenVerificationMiddleware")

        try:
            if not is_unprotected_path(request.url.path):
                check_headers_token(request)
                token = extract_token(request)
                logging.info(f"token: {token}")
                token_info = get_token_info(token)
                check_token(token_info)
                state_token_info = generate_state_info(token_info)
                store_token_info_in_state(state_token_info, request)
            response = await call_next(request)
            return response
        except HTTPException as exc:
            return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
