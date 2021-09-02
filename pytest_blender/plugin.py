"""pytest-blender plugin"""

import io
import os
import subprocess
import sys

import pytest

from pytest_blender.utils import which_blender_by_os


def pytest_addoption(parser):
    parser.addoption(
        "--blender-executable",
        nargs=1,
        default=which_blender_by_os,
        help="Blender executable location.",
    )


def _get_blender_executable(config):
    blender_executable = config.getoption("--blender-executable")
    if hasattr(blender_executable, "__call__"):
        return blender_executable()
    return blender_executable[0]


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    # build propagated CLI args
    propagated_cli_args = []
    _inside_root_invocation_arg = False
    for arg in sys.argv[1:]:
        if _inside_root_invocation_arg:
            _inside_root_invocation_arg = False
            continue
        elif arg == "--blender-executable":
            _inside_root_invocation_arg = True
            continue
        propagated_cli_args.append(arg)

    blender_executable = _get_blender_executable(config)

    if not blender_executable:
        pytest.exit("'blender' executable not found.", returncode=1)

    # run pytest using blender
    proc = subprocess.Popen(
        [
            blender_executable,
            "-b",
            "--python",
            os.path.join(
                os.path.abspath(os.path.dirname(__file__)),
                "run_pytest.py",
            ),
            "--",
            "--pytest-blender-executable",
            blender_executable,
            *propagated_cli_args,  # propagate command line arguments
        ],
        stdout=sys.stdout,
        stderr=sys.stderr,
    )
    proc.communicate()

    # hide "Exit:" message shown by pytest on exit
    sys.stderr = io.StringIO()
    pytest.exit("", returncode=proc.returncode)
