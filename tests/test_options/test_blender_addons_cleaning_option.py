import os
import shutil

import pytest
from testing_utils import ADDONS_DIRS, EXPECTED_ADDONS

from pytest_blender.utils import get_addons_dir, which_blender


BLENDER_USER_ADDONS_DIR = get_addons_dir(which_blender())
BAR_ADDONS_DIR = os.path.join(ADDONS_DIRS, "bar")


parametrize_uninstall_cleaning_args = pytest.mark.parametrize(
    "cleaning_args",
    (
        pytest.param([], id="cleaning_args=[]"),
        pytest.param(
            ["--blender-addons-cleaning", "uninstall"],
            id='cleaning_args=["--blender-addons-cleaning", "uninstall"]',
        ),
    ),
)


def render_addon_installation_test():
    return """def test_pytest_blender_basic_installed():
    import addon_utils
    installed_addons = [addon.__name__ for addon in addon_utils.modules()]
    assert "pytest_blender_basic" in installed_addons
"""


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


@parametrize_uninstall_cleaning_args
def test_blender_addons_cleaning_cli_option_default(testing_context, cleaning_args):
    clean_addons()

    with testing_context(
        force_empty_inicfg=True,
        files={"tests/test_addon_installed.py": render_addon_installation_test()},
    ) as ctx:
        _, stderr, exitcode = ctx.run(
            ["--blender-addons-dirs", BAR_ADDONS_DIR, *cleaning_args]
        )
        assert exitcode == 0, stderr

    # by default is uninstall, so the addon must not be in the addons dir
    assert os.listdir(BAR_ADDONS_DIR)[0] not in os.listdir(BLENDER_USER_ADDONS_DIR)


def test_blender_addons_cleaning_cli_option_disable(testing_context):
    clean_addons()

    with testing_context(
        force_empty_inicfg=True,
        files={"tests/test_addon_installed.py": render_addon_installation_test()},
    ) as ctx:
        _, stderr, exitcode = ctx.run(
            [
                "--blender-addons-dirs",
                BAR_ADDONS_DIR,
                "--blender-addons-cleaning",
                "disable",
            ]
        )
        assert exitcode == 0, stderr

    assert "pytest_blender_basic.py" in os.listdir(BLENDER_USER_ADDONS_DIR)
    clean_addons()
    assert "pytest_blender_basic.py" not in os.listdir(BLENDER_USER_ADDONS_DIR)


def test_blender_addons_cleaning_cli_option_keep(testing_context):
    clean_addons()

    with testing_context(
        force_empty_inicfg=True,
        files={"tests/test_addon_installed.py": render_addon_installation_test()},
    ) as ctx:
        _, stderr, exitcode = ctx.run(
            [
                "--blender-addons-dirs",
                BAR_ADDONS_DIR,
                "--blender-addons-cleaning",
                "keep",
            ]
        )
        assert exitcode == 0, stderr

    assert "pytest_blender_basic.py" in os.listdir(BLENDER_USER_ADDONS_DIR)

    with testing_context(
        force_empty_inicfg=True,
        files={"tests/test_addon_installed.py": render_addon_installation_test()},
    ) as ctx:
        _, stderr, exitcode = ctx.run()
        assert exitcode == 0, stderr

    assert "pytest_blender_basic.py" in os.listdir(BLENDER_USER_ADDONS_DIR)
    clean_addons()


@parametrize_uninstall_cleaning_args
def test_blender_addons_cleaning_inicfg_default_option(testing_context, cleaning_args):
    clean_addons()

    blender_addons_cleaning_config = (
        "\nblender-addons-cleaning = uninstall" if len(cleaning_args) else ""
    )

    with testing_context(
        files={
            "tests/test_addon_installed.py": render_addon_installation_test(),
            "pytest.ini": f"""[pytest]{blender_addons_cleaning_config}
blender-addons-dirs = {BAR_ADDONS_DIR}
""",
        },
    ) as ctx:
        _, stderr, exitcode = ctx.run()
        assert exitcode == 0, stderr

    assert os.listdir(BAR_ADDONS_DIR)[0] not in os.listdir(BLENDER_USER_ADDONS_DIR)


def test_blender_addons_cleaning_inicfg_disable_option(testing_context):
    clean_addons()

    with testing_context(
        files={
            "tests/test_addon_installed.py": render_addon_installation_test(),
            "pytest.ini": f"""[pytest]
blender-addons-cleaning = disable
blender-addons-dirs = {BAR_ADDONS_DIR}
""",
        },
    ) as ctx:
        _, stderr, exitcode = ctx.run()
        assert exitcode == 0, stderr

    assert "pytest_blender_basic.py" in os.listdir(BLENDER_USER_ADDONS_DIR)
    clean_addons()
    assert "pytest_blender_basic.py" not in os.listdir(BLENDER_USER_ADDONS_DIR)


def test_blender_addons_cleaning_inicfg_option_keep(testing_context):
    clean_addons()

    with testing_context(
        files={
            "pytest.ini": f"""[pytest]
blender-addons-cleaning = keep
blender-addons-dirs = {BAR_ADDONS_DIR}
""",
            "tests/test_addon_installed.py": render_addon_installation_test(),
        },
    ) as ctx:
        _, stderr, exitcode = ctx.run()
        assert exitcode == 0, stderr

    assert "pytest_blender_basic.py" in os.listdir(BLENDER_USER_ADDONS_DIR)

    with testing_context(
        force_empty_inicfg=True,
        files={"tests/test_addon_installed.py": render_addon_installation_test()},
    ) as ctx:
        _, stderr, exitcode = ctx.run()
        assert exitcode == 0, stderr

    assert "pytest_blender_basic.py" in os.listdir(BLENDER_USER_ADDONS_DIR)
    clean_addons()
