"""pytest-blender tests configuration."""

import logging
import os


ROOT_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
DATA_DIR = os.path.join(ROOT_DIR, "tests", "data")
ADDONS_DIR = os.path.join(ROOT_DIR, "tests", "addons")

pytest_blender_logger = logging.getLogger("pytest_blender")
pytest_blender_logger.setLevel(logging.DEBUG)
pytest_blender_logger.addHandler(logging.StreamHandler())

try:
    from pytest_blender import utils
except ImportError:
    pass
else:
    # create zipped addon from data
    addon_id = "pytest_blender_zipped"
    zipped_filepath = os.path.join(ADDONS_DIR, f"{addon_id}.zip")
    if os.path.isfile(zipped_filepath):
        os.remove(zipped_filepath)

    addon_to_zip_dirpath = os.path.join(DATA_DIR, addon_id)
    utils.zipify_addon_package(addon_to_zip_dirpath, ADDONS_DIR)
