import logging
from fastapi import status, Request, HTTPException
from functools import wraps
from typing import List


def check_roles( list_roles: list, permissions: List[str] ) -> None:
    if not any(perm in list_roles for perm in permissions):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions ! "
                   "Need : " + ", ".join(permissions) +
                   " / Got : " + ", ".join(list_roles)
        )


def check_permissions( permissions: List[str] ):
    def decorator( func ):
        @wraps(func)
        async def wrapper( request: Request, *args, **kwargs ):
            logging.info(f"Checking permissions {permissions}")
            logging.info(f"License: {request}")

            check_roles(request.state.token_info.get('license_roles'), permissions)

            return await func(request, *args, **kwargs)

        return wrapper

    return decorator
