"""pytest-blender tests configuration."""

import logging
import os

import pytest


ROOT_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
DATA_DIR = os.path.join(ROOT_DIR, "tests", "data")
ADDONS_DIR = os.path.join(ROOT_DIR, "tests", "addons")

pytest_blender_logger = logging.getLogger("pytest_blender")
pytest_blender_logger.setLevel(logging.DEBUG)
pytest_blender_logger.addHandler(logging.StreamHandler())

try:
    from pytest_blender.test import pytest_blender_active
except ImportError:
    # executing pytest from Python Blender executable, the plugin is active
    pytest_blender_active = True

if pytest_blender_active:

    @pytest.fixture(scope="session", autouse=True)
    def create_zipped_addon(zipify_addon_package):
        # create zipped addon from data
        addon_id = "pytest_blender_zipped"
        zipped_filepath = os.path.join(ADDONS_DIR, f"{addon_id}.zip")
        if os.path.isfile(zipped_filepath):
            os.remove(zipped_filepath)

        addon_to_zip_dirpath = os.path.join(DATA_DIR, addon_id)
        zipify_addon_package(addon_to_zip_dirpath, ADDONS_DIR)

        print("ADDONS_DIR", os.listdir(ADDONS_DIR))
