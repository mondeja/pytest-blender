"""pytest-blender tests configuration."""

import logging
import os
import sys
import zipfile

import pytest


TESTS_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(TESTS_DIR, "data")
ADDONS_DIR = os.path.join(
    TESTS_DIR,
    "addons",
)

pytest_blender_logger = logging.getLogger("pytest_blender")
pytest_blender_logger.setLevel(logging.DEBUG)
pytest_blender_logger.addHandler(logging.StreamHandler())


def zipify_addon_dir(in_dirpath, out_dirpath):
    addon_zipped_path = os.path.join(
        out_dirpath,
        f"{os.path.basename(in_dirpath)}.zip",
    )

    with zipfile.ZipFile(addon_zipped_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(in_dirpath):
            for file in files:
                zipf.write(
                    os.path.join(root, file),
                    os.path.relpath(
                        os.path.join(root, file),
                        os.path.join(in_dirpath, ".."),
                    ),
                )
    return addon_zipped_path


try:
    from pytest_blender.test import pytest_blender_active
except ImportError:
    # executing pytest from Python Blender executable, the plugin is active
    pytest_blender_active = True

if pytest_blender_active:

    @pytest.fixture(scope="session", autouse=True)
    def create_zipped_addon():
        # create zipped addon from data
        addon_to_zip_dirpath = os.path.join(DATA_DIR, "pytest_blender_zipped")
        zipify_addon_dir(addon_to_zip_dirpath, ADDONS_DIR)
