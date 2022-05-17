import os

import pytest
from testing_utils import (
    ADDONS_DIRS,
    EXPECTED_ADDONS,
    executable_param_id,
    parametrize_plugin_on_off_with,
)


def addons_dict_from_ids(addons_ids):
    addons_dict = {}
    for addon_id in addons_ids:
        if addon_id not in EXPECTED_ADDONS:
            raise ValueError(
                f"Addon '{addon_id}' not found in expected addons dictionary"
            )
        addons_dict[addon_id] = EXPECTED_ADDONS[addon_id]
    return addons_dict


def render_addons_installed_test(expected_addons_ids):
    return f"""def test_addons_installed():
    import addon_utils
    import bpy

    expected_addons = {addons_dict_from_ids(expected_addons_ids)}

    installed_addons = [addon.__name__ for addon in addon_utils.modules()]
    assert "__init__" not in installed_addons

    operator_classes = [cls.__name__ for cls in bpy.types.Operator.__subclasses__()]

    for addon_id, operator_class in expected_addons.items():
        assert addon_id in installed_addons
        assert operator_class in operator_classes
"""


FOO_ADDONS_DIR = ["pytest_blender_zipped", "pytest_blender_zipped_from_dir"]
FOO_BAR_ADDONS_DIR = list(EXPECTED_ADDONS)

parametrize_addons_dirs = pytest.mark.parametrize(
    ("addons_dirs", "addons_ids"),
    (
        pytest.param(
            [os.path.join(ADDONS_DIRS, "foo")],
            FOO_ADDONS_DIR,
            id=f'addons_dirs=["foo"]-addons_ids={executable_param_id(FOO_ADDONS_DIR)}',
        ),
        pytest.param(
            [os.path.join(ADDONS_DIRS, "foo"), os.path.join(ADDONS_DIRS, "bar")],
            FOO_BAR_ADDONS_DIR,
            id=(
                'addons_dirs=["foo", "bar"]'
                f"-addons_ids={executable_param_id(FOO_BAR_ADDONS_DIR)}"
            ),
        ),
    ),
)


@parametrize_plugin_on_off_with(expected_exitcode_when_off=4)
@parametrize_addons_dirs
def test_blender_addons_dirs_cli_option(
    testing_context, plugin_args, addons_dirs, addons_ids, expected_exitcode
):
    with testing_context(
        {
            "tests/test_blender_addons_dirs_cli_option.py": (
                render_addons_installed_test(addons_ids)
            ),
        },
    ) as ctx:
        _, stderr, exitcode = ctx.run(
            [
                "--noconftest",
                "tests",
                *plugin_args,
                "--blender-addons-dirs",
                *addons_dirs,
            ]
        )
        assert exitcode == expected_exitcode, stderr


@parametrize_plugin_on_off_with(expected_exitcode_when_off=4)
@parametrize_addons_dirs
def test_blender_addons_dirs_inicfg_option(
    testing_context, plugin_args, addons_dirs, addons_ids, expected_exitcode
):
    if len(addons_dirs) == 1:
        addons_dirs_inicfg_value = f"{addons_dirs[0]}\n"
    else:
        addons_dirs_inicfg_value = "\n"
        for addons_dir in addons_dirs:
            addons_dirs_inicfg_value += f"    {addons_dir}\n"
    with testing_context(
        files={
            "tests/test_blender_addons_dirs_inicfg_option.py": (
                render_addons_installed_test(addons_ids)
            ),
            "pytest.ini": f"[pytest]\nblender-addons-dirs = {addons_dirs_inicfg_value}",
        },
    ) as ctx:
        _, stderr, exitcode = ctx.run(plugin_args)
        assert exitcode == expected_exitcode, stderr
