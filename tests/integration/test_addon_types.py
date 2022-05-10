import io
import logging
import os
from contextlib import redirect_stdout

import pytest
import addon_utils

pytest_blender_logger = logging.getLogger("pytest_blender")
pytest_blender_logger.setLevel(logging.DEBUG)
pytest_blender_logger.addHandler(logging.StreamHandler())


addons_dir = os.path.join(
    os.path.abspath(os.path.dirname(__file__).rsplit('/', 1)[0]),  # rsplit for getting parent directory
    "addons",
)


def test_register_archived_addon(install_addons_from_dir, disable_addons):
    addon_name = 'archived-addon'
    addon_filepath = os.path.join(addons_dir, 'archived-addon.zip')
    f = io.StringIO()
    with redirect_stdout(f):
        assert os.path.isfile(addon_filepath) == True
        addon_module_names = install_addons_from_dir(addons_dir, 'archived-addon.zip')
        installed_addons = [addon.bl_info.get('name', None) for addon in addon_utils.modules()]
        assert "Move X Axis (archived)" in installed_addons
    with redirect_stdout(f):
        disable_addons(addon_module_names)


def test_register_addon_with_version_postfix(install_addons_from_dir, disable_addons):
    addon_name = 'pytest_blender_basic-1.2.3'
    addon_filepath = os.path.join(addons_dir, 'pytest_blender_basic-1.2.3.py')
    f = io.StringIO()
    with redirect_stdout(f):
        assert os.path.isfile(addon_filepath) == True
        addon_module_names = install_addons_from_dir(addons_dir, [(addon_name, addon_filepath)])
        installed_addons = [addon.bl_info.get('name', None) for addon in addon_utils.modules()]
        assert "Move X Axis 1.2.3" in installed_addons
    with redirect_stdout(f):
        disable_addons(addon_module_names)
        