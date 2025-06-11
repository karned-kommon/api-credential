import logging
from datetime import datetime, timezone

import httpx
from fastapi import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from decorators.log_time import log_time_async
from middlewares.token_middleware import read_cache_token, write_cache_token
from services.inmemory_service import get_redis_api_db
from utils.path_util import is_unprotected_path, is_unlicensed_path
from config.config import URL_API_GATEWAY


r = get_redis_api_db()


def extract_licence(request: Request) -> str:
    return request.headers.get('X-License-Key')


def is_headers_licence_present(request: Request) -> bool:
    licence = extract_licence(request)
    if not licence:
        return False
    return True


def check_headers_licence(request: Request) -> None:
    if not is_headers_licence_present(request):
        raise HTTPException(status_code=403, detail="Licence header missing")


def is_licence_found(request: Request, licence: str) -> bool:
    logging.info(f"License : is_licence_found")
    licenses = getattr(request.state, 'licenses', None)
    if not licenses:
        return False

    # Check if any valid license matches the requested license
    for licence_data in licenses:
        # Skip if licence_data is not a dictionary
        if not isinstance(licence_data, dict):
            logging.warning(f"Skipping non-dictionary license in is_licence_found: {licence_data}")
            continue

        # Use get() to safely access the uuid
        if licence_data.get('uuid') == licence:
            return True

    return False


def get_licences(token: str) -> list:
    logging.info(f"License : get_licences")
    response = httpx.get(f"{URL_API_GATEWAY}/license/v1/mine", headers={"Authorization": f"Bearer {token}"})
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Licences request failed")
    data = response.json()
    return data.get("data", [])


def filter_licences(licences: list) -> list:
    now = int(datetime.now(timezone.utc).timestamp())
    licences_filtered = []

    for lic in licences:
        # Skip if lic is not a dictionary
        if not isinstance(lic, dict):
            logging.warning(f"Skipping non-dictionary license: {lic}")
            continue

        # Skip if required fields are missing
        if "iat" not in lic or "exp" not in lic:
            logging.warning(f"Skipping license missing required fields: {lic}")
            continue

        # Skip if license is not valid (outside time range)
        if not (lic["iat"] < now < lic["exp"]):
            continue

        licences_filtered.append({
            "uuid": lic.get("uuid"),
            "type_uuid": lic.get("type_uuid"),
            "name": lic.get("name"),
            "iat": lic.get("iat"),
            "exp": lic.get("exp"),
            "entity_uuid": lic.get("entity_uuid"),
            "api_roles": lic.get("api_roles"),
            "app_roles": lic.get("app_roles"),
            "apps": lic.get("apps"),
        })

    return licences_filtered


def prepare_licences(token: str) -> list:
    licenses = get_licences(token)
    return filter_licences(licenses)


def refresh_cache_token(request: Request) -> dict:
    logging.info(f"License : refresh_cache_token")
    cache_token = read_cache_token(getattr(request.state, 'token', None))
    cache_token['licenses'] = getattr(request.state, 'licenses', None)
    logging.info(f"cache_token: {cache_token}")
    return cache_token


def refresh_licences(request: Request) -> None:
    logging.info(f"License : refresh_licences")
    token = getattr(request.state, 'token', None)
    licenses = prepare_licences(token)
    setattr(request.state, 'licenses', licenses)
    write_cache_token(token=token, cache_token=refresh_cache_token(request))


def check_licence(request: Request, licence: str) -> None:
    if not is_licence_found(request, licence):
        refresh_licences(request)
        if not is_licence_found(request, licence):
            raise HTTPException(status_code=403, detail="Licence not found")


def extract_entity(request: Request) -> str:
    licenses = getattr(request.state, 'licenses', None)
    license_uuid = getattr(request.state, 'licence_uuid', None)

    if not licenses:
        raise HTTPException(status_code=500, detail="No licenses found")

    for lic in licenses:
        # Skip if lic is not a dictionary
        if not isinstance(lic, dict):
            logging.warning(f"Skipping non-dictionary license in extract_entity: {lic}")
            continue

        if str(lic.get('uuid', '')) == str(license_uuid):
            entity_uuid = lic.get('entity_uuid')
            if entity_uuid:
                return entity_uuid

    raise HTTPException(status_code=500, detail="Entity not found")


class LicenceVerificationMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

    @log_time_async
    async def dispatch(self, request: Request, call_next) -> Response:
        logging.info("LicenceVerificationMiddleware")
        try:
            if not is_unprotected_path(request.url.path) and not is_unlicensed_path(request.url.path):
                check_headers_licence(request)
                licence_uuid = extract_licence(request)
                logging.info(f"licence_uuid: {licence_uuid}")
                check_licence(request, licence_uuid)
                setattr(request.state, 'licence_uuid', licence_uuid)
                entity_uuid = extract_entity(request)
                logging.info(f"entity_uuid: {entity_uuid}")
                setattr(request.state, 'entity_uuid', entity_uuid)
            response = await call_next(request)
            return response
        except HTTPException as exc:
            return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
