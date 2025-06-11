import tests.env_setup
import pytest
from utils.path_util import is_unprotected_path, is_unlicensed_path
from config.config import UNPROTECTED_PATHS, UNLICENSED_PATHS


class TestPathUtil:
    def test_is_unprotected_path_true(self):
        # Test with a path that is in UNPROTECTED_PATHS
        assert is_unprotected_path(UNPROTECTED_PATHS[0]) is True

    def test_is_unprotected_path_false(self):
        # Test with a path that is not in UNPROTECTED_PATHS
        assert is_unprotected_path("/some-random-path") is False

    def test_is_unlicensed_path_true(self):
        # Since UNLICENSED_PATHS might be empty, we'll mock it for this test
        with pytest.MonkeyPatch().context() as m:
            m.setattr("utils.path_util.UNLICENSED_PATHS", ["/unlicensed-path"])
            assert is_unlicensed_path("/unlicensed-path") is True

    def test_is_unlicensed_path_false(self):
        # Test with a path that is not in UNLICENSED_PATHS
        assert is_unlicensed_path("/some-random-path") is False
