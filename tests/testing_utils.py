import os

import pytest


TESTS_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(TESTS_DIR, "data")
ADDONS_DIRS = os.path.join(TESTS_DIR, "addons-dirs")

EXPECTED_ADDONS = {
    "pytest_blender_basic": "PytestBlenderBasicObjectMoveX",
    "pytest_blender_zipped": "PytestBlenderZippedObjectMoveX",
    "pytest_blender_zipped_from_dir": "PytestBlenderZippedFromDirObjectMoveX",
}


def parametrize_plugin_on_off_with(expected_exitcode_when_off=1):
    return pytest.mark.parametrize(
        ("plugin_args", "expected_exitcode"),
        (
            pytest.param([], 0, id="plugin_args=[]-exitcode=0"),
            pytest.param(
                ["-p", "no:pytest-blender"],
                expected_exitcode_when_off,
                id=(
                    'plugin_args=["-p", "no:pytest-blender"]'
                    f"-exitcode={expected_exitcode_when_off}"
                ),
            ),
        ),
    )


parametrize_plugin_on_off = parametrize_plugin_on_off_with()


executable_param_id = lambda x: str(x).replace("'", '"')
