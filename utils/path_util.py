from config.config import UNPROTECTED_PATHS


def is_unprotected_path( path: str ) -> bool:
    return path.lower() in UNPROTECTED_PATHS