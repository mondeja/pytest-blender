import functools
import os
import shutil

import pytest

from pytest_blender.utils import get_addons_dir, which_blender


TESTS_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(TESTS_DIR, "data")
ADDONS_DIRS = os.path.join(TESTS_DIR, "addons-dirs")

EXPECTED_ADDONS = {
    "pytest_blender_basic": "PytestBlenderBasicObjectMoveX",
    "pytest_blender_zipped": "PytestBlenderZippedObjectMoveX",
    "pytest_blender_zipped_from_dir": "PytestBlenderZippedFromDirObjectMoveX",
}

BLENDER_USER_ADDONS_DIR = get_addons_dir(which_blender())


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


def _render_addon_installation_test(comparison, addon_id):
    return f"""def test_addon_installed():
    import addon_utils
    installed_addons = [addon.__name__ for addon in addon_utils.modules()]
    assert "{addon_id}" {comparison} installed_addons
"""


render_addon_installed_test = functools.partial(_render_addon_installation_test, "in")
render_addon_not_installed_test = functools.partial(
    _render_addon_installation_test, "not in"
)


def clean_addons():
    for addon_id in EXPECTED_ADDONS:
        py_module_addon_path = os.path.join(
            BLENDER_USER_ADDONS_DIR,
            f"{addon_id}.py",
        )
        if os.path.isfile(py_module_addon_path):
            os.remove(py_module_addon_path)
            continue

        py_package_addon_path = os.path.join(
            BLENDER_USER_ADDONS_DIR,
            addon_id,
        )
        if os.path.isdir(py_package_addon_path) and os.path.isfile(
            os.path.join(py_package_addon_path, "__init__.py")
        ):
            shutil.rmtree(py_package_addon_path)
            continue
