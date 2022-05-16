"""pytest-blender tests configuration."""

import contextlib
import os
import subprocess
import sys
import tempfile

import pytest


ROOT_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
TESTS_DIR = os.path.join(ROOT_DIR, "tests")
DATA_DIR = os.path.join(TESTS_DIR, "data")
ADDONS_DIR = os.path.join(TESTS_DIR, "addons")

if TESTS_DIR not in sys.path:
    sys.path.append(TESTS_DIR)

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


@pytest.fixture
def testing_context():
    @contextlib.contextmanager
    def _testing_context(files={}):
        with tempfile.TemporaryDirectory() as root_dirpath:
            for rel_filepath, content in files.items():
                filepath = os.path.join(root_dirpath, rel_filepath)

                # ensure that its directory exists
                basedir = os.path.abspath(os.path.dirname(filepath))
                os.makedirs(basedir)

                with open(filepath, "w") as f:
                    f.write(content)

            def run_in_context(additional_pytest_args=[], **kwargs):
                with subprocess.Popen(
                    [
                        sys.executable,
                        "-mpytest",
                        "-svv",
                        "--strict-markers",
                        "--strict-config",
                        *additional_pytest_args,
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=root_dirpath,
                    **kwargs,
                ) as proc:
                    stdout, stderr = proc.communicate()
                    return stdout, stderr, proc.returncode

            yield type(
                "PytestBlenderTestingContext",
                (),
                {
                    "run": run_in_context,
                },
            )

    return _testing_context
