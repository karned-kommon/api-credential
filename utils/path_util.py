from config.config import UNPROTECTED_PATHS, UNLICENSED_PATHS


def is_unprotected_path( path: str ) -> bool:
    return path.lower() in UNPROTECTED_PATHS

def is_unlicensed_path( path: str ) -> bool:
    return path.lower() in UNLICENSED_PATHS