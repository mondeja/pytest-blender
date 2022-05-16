"""pytest-blender tests configuration."""

import os

import pytest


ROOT_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
DATA_DIR = os.path.join(ROOT_DIR, "tests", "data")
ADDONS_DIR = os.path.join(ROOT_DIR, "tests", "addons")

try:
    from pytest_blender import zipify_addon_package
except ImportError:
    inside_blender_interpreter = True
else:
    inside_blender_interpreter = False

    # create zipped addon from data
    addon_id = "pytest_blender_zipped"
    zipped_filepath = os.path.join(ADDONS_DIR, f"{addon_id}.zip")
    if os.path.isfile(zipped_filepath):
        os.remove(zipped_filepath)

    addon_to_zip_dirpath = os.path.join(DATA_DIR, addon_id)
    zipify_addon_package(addon_to_zip_dirpath, ADDONS_DIR)


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "blender: skip test if not running inside Python's Blender interpreter",
    )


def pytest_runtest_setup(item):
    if not inside_blender_interpreter and list(item.iter_markers("blender")):
        pytest.skip("The plugin 'pytest-blender' is required to run this test")
