import os
import shutil

from testing_utils import (
    ADDONS_DIRS,
    BLENDER_USER_ADDONS_DIR,
    clean_addons,
    render_addon_installed_test,
    render_addon_not_installed_test,
)


FOO_ADDONS_DIR = os.path.join(ADDONS_DIRS, "foo")


def test_install_addons_from_dir_fixture(testing_context):
    clean_addons()

    with testing_context(
        empty_inicfg=True,
        files={
            "tests/conftest.py": f"""
import pytest

@pytest.fixture(scope="session", autouse=True)
def install_addons(install_addons_from_dir, uninstall_addons):
    addons_ids = install_addons_from_dir(
        "{FOO_ADDONS_DIR}",
        addons_ids=['pytest_blender_zipped'],
    )
    yield
    uninstall_addons(addons_ids)
""",
            "tests/test_addon_installed.py": render_addon_installed_test(
                "pytest_blender_zipped"
            ),
            "tests/test_addon_not_installed.py": render_addon_not_installed_test(
                "pytest_blender_zipped_from_dir"
            ),
        },
    ) as ctx:
        _, stderr, exitcode = ctx.run()
        assert exitcode == 0, stderr

    assert "pytest_blender_zipped" not in os.listdir(BLENDER_USER_ADDONS_DIR)
    assert "pytest_blender_zipped_from_dir" not in os.listdir(BLENDER_USER_ADDONS_DIR)


def test_install_addons_from_dir_invalid_addon(testing_context):
    """When an invalid addon is found in the addons directory, must be
    ignored.

    An addon could be invalid if:

    - It hasn't a `bl_info` attribute.
    """
    clean_addons()

    with testing_context(
        empty_inicfg=True,
        files={
            "conftest.py": """
import os
import pytest

@pytest.fixture(scope="session", autouse=True)
def install_addons(install_addons_from_dir, uninstall_addons):
    addons_ids = install_addons_from_dir(
        os.getcwd(),
        addons_ids=['pytest_blender_zipped', 'helpers'],
    )
    yield
    uninstall_addons(addons_ids)
""",
            "tests/test_addon_installed.py": render_addon_installed_test(
                "pytest_blender_zipped"
            ),
            "tests/test_addon_not_installed.py": render_addon_not_installed_test(
                "helpers"
            ),
        },
    ) as ctx:
        shutil.copyfile(
            os.path.join(FOO_ADDONS_DIR, "pytest_blender_zipped.zip"),
            os.path.join(ctx.rootdir, "pytest_blender_zipped.zip"),
        )
        with open(os.path.join(ctx.rootdir, "helpers.py"), "w") as f:
            f.write('import sys\nsys.stdout.write("HELPERS")\n')

        stdout, stderr, exitcode = ctx.run()
        assert exitcode == 0, f"{stdout}\n{stderr}\n"
        assert (
            "[pytest-blender]"
            " Skipping installation of module 'helpers' as is not a"
            " Blender addon (missing 'bl_info' module attribute)"
        ) in stdout

    assert "pytest_blender_zipped" not in os.listdir(BLENDER_USER_ADDONS_DIR)
    assert "helpers.py" not in BLENDER_USER_ADDONS_DIR
