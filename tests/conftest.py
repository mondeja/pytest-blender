"""pytest-blender tests configuration."""

import contextlib
import copy
import os
import subprocess
import sys
import tempfile

import pytest


TESTS_DIR = os.path.abspath(os.path.dirname(__file__))
if TESTS_DIR not in sys.path:
    sys.path.append(TESTS_DIR)
from testing_utils import ADDONS_DIRS, DATA_DIR


try:
    from pytest_blender import zipify_addon_package
except ImportError:
    inside_blender_interpreter = True
else:
    inside_blender_interpreter = False

    # create zipped addon from data
    addon_id = "pytest_blender_zipped"
    foo_addons_dir = os.path.join(ADDONS_DIRS, "foo")
    zipped_filepath = os.path.join(foo_addons_dir, f"{addon_id}.zip")
    if os.path.isfile(zipped_filepath):
        os.remove(zipped_filepath)

    addon_to_zip_dirpath = os.path.join(DATA_DIR, addon_id)
    zipify_addon_package(addon_to_zip_dirpath, foo_addons_dir)


@pytest.fixture
def testing_context():
    @contextlib.contextmanager
    def _testing_context(files={}, empty_inicfg=False):
        with tempfile.TemporaryDirectory() as rootdir:
            # we need to force an empty ini file because pytest caches the
            # `setup.cfg` ini file used to execute the test suite itself,
            # reusing it so executing tests with `addopts` option defined
            if empty_inicfg:
                files["pytest.ini"] = "[pytest]\n"

            for rel_filepath, content in files.items():
                filepath = os.path.join(rootdir, rel_filepath)

                # ensure that its directory exists
                basedir = os.path.abspath(os.path.dirname(filepath))
                os.makedirs(basedir, exist_ok=True)

                with open(filepath, "w") as f:
                    f.write(content)

            def run_in_context(
                additional_pytest_args=None,
                additional_blender_args=None,
                env=None,
                cmd_prefix=None,
                **kwargs,
            ):
                if cmd_prefix is None:
                    cmd_prefix = [sys.executable]

                if env is None:
                    env = {}

                _env = copy.copy(os.environ)
                if "PWD" in _env:
                    _env["PWD"] = rootdir
                _env.update(env)

                if additional_pytest_args is None:
                    additional_pytest_args = []

                if "-c" not in additional_pytest_args and "pytest.ini" in files:
                    additional_pytest_args = copy.copy(additional_pytest_args)
                    additional_pytest_args.extend(
                        ["-c", os.path.join(rootdir, "pytest.ini")]
                    )

                if additional_blender_args is None:
                    additional_blender_args = []
                else:
                    additional_blender_args.insert(0, "--")

                cmd = [
                    *cmd_prefix,
                    "-m",
                    "pytest",
                    "-svv",
                    f"--rootdir={rootdir}",
                    "--strict-markers",
                    "--strict-config",
                    *additional_pytest_args,
                ]
                with subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=rootdir,
                    env=_env,
                    **kwargs,
                ) as proc:
                    stdout, stderr = proc.communicate()
                    return (
                        stdout.decode("utf-8"),
                        stderr.decode("utf-8"),
                        proc.returncode,
                    )

            ctx = type(
                "PytestBlenderTestingContext",
                (),
                {
                    "run": run_in_context,
                },
            )
            ctx.rootdir = rootdir
            yield ctx

    return _testing_context
