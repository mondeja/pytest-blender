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
    parser.addoption(
        "--blender-template",
        nargs=1,
        default=None,
        help="Open Blender using an empty layout as start template.",
    )


def _get_blender_executable(config):
    blender_executable = config.getoption("--blender-executable")
    if hasattr(blender_executable, "__call__"):
        return blender_executable()
    return blender_executable[0]


def _add_template_arg(config, args):
    template = config.getoption("--blender-template")
    if template:
        args.append(template[0])


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    pytest_help_opt = False

    # build propagated CLI args
    args_groups, args_group_index = ([], [], []), 0
    argv = sys.argv[1:]
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg in ["--blender-executable", "--blender-template"]:
            i += 2
            continue
        elif arg in ["-h", "--help"]:
            pytest_help_opt = True
            break
        elif arg == "--":
            args_group_index += 1
            i += 1
            continue
        args_groups[args_group_index].append(arg)
        i += 1

    if pytest_help_opt:
        return

    blender_executable = _get_blender_executable(config)

    if not blender_executable:
        pytest.exit("'blender' executable not found.", returncode=1)

    pytest_opts, blender_opts, python_opts = args_groups

    # run pytest using blender
    args = [
        blender_executable,
        "-b",
    ]

    # template to open
    _add_template_arg(config, args)

    args.extend(
        [
            *blender_opts,  # propagate Blender command line arguments
            "--python",
            os.path.join(
                os.path.abspath(os.path.dirname(__file__)),
                "run_pytest.py",
            ),
            *python_opts,  # propagate Python command line arguments
            "--",
            "--pytest-blender-executable",
            blender_executable,
            *pytest_opts,  # propagate Pytest command line arguments
        ]
    )
    proc = subprocess.Popen(args, stdout=sys.stdout, stderr=sys.stderr)
    proc.communicate()

    # hide "Exit:" message shown by pytest on exit
    sys.stderr = io.StringIO()
    pytest.exit("", returncode=proc.returncode)
