"""pytest-blender plugin"""

import io
import logging
import os
import signal
import subprocess
import sys

import pytest

from pytest_blender.utils import which_blender_by_os


logger = logging.getLogger("pytest-blender")

OPTIONS = {
    "blender-executable": {"help": "Blender executable location."},
    "blender-template": {
        "help": "Open Blender using an empty layout as start template."
    },
    "blender-addons-dirs": {
        "help": "Directory with addons to install for testing them.",
        "opts": {"nargs": "+", "default": []},
    },
}


def get_blender_executable(config):
    # from CLI
    blender_executable = config.getoption("--blender-executable")
    if blender_executable is not None:
        return blender_executable

    # from inicfg
    if "blender-executable" in config.inicfg:
        return config.inicfg["blender-executable"]

    # discover from system
    return which_blender_by_os()


def get_addons_dir(config):
    # from CLI
    # --blender-addons-dirs tests/addons tests/other
    addons_dirs = config.getoption("--blender-addons-dirs")
    if addons_dirs:
        return [os.path.abspath(d) for d in addons_dirs]

    # from inicfg
    if "blender-addons-dirs" not in config.inicfg:
        return []
    addons_dirs = config.inicfg["blender-addons-dirs"]
    if "\n" in addons_dirs:
        addons_dirs = addons_dirs.split("\n")
    else:  # passed as str
        addons_dirs = [addons_dirs]
    return [os.path.abspath(d) for d in addons_dirs if d]


def add_template_arg(config, args):
    template = config.getoption("--blender-template")
    if template:
        args.append(os.path.abspath(template))
    elif "blender-template" in config.inicfg:
        args.append(os.path.abspath(config.inicfg["blender-template"]))


@pytest.hookimpl(tryfirst=True)
def pytest_addoption(parser):
    for arg, argdef in OPTIONS.items():
        kwargs = argdef["opts"] if "opts" in argdef else {"default": None}
        parser.addoption(f"--{arg}", help=argdef["help"], **kwargs)
        parser.addini(arg, argdef["help"])


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    from pprint import pprint

    print(config.inicfg)

    pytest_help_opt = False

    # build propagated CLI args
    args_groups, args_group_index = ([], [], []), 0
    argv = sys.argv[1:]
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg in OPTIONS.keys():
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

    blender_executable = get_blender_executable(config)

    if not blender_executable:
        pytest.exit("'blender' executable not found.", returncode=1)

    # process subprocess arguments
    pytest_opts, blender_opts, python_opts = args_groups

    # run pytest using blender
    args = [blender_executable, "-b"]

    # template to open
    add_template_arg(config, args)

    # addons directory to install them
    addons_dirs_args = []
    for addons_dir in get_addons_dir(config):
        addons_dirs_args.extend(["--pytest-blender-addons-dir", addons_dir])
    print(addons_dirs_args)

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
            "--pytest-blender-inicfg-options",
            ",".join(list(OPTIONS.keys())),
            *addons_dirs_args,
            *pytest_opts,  # propagate Pytest command line arguments
        ]
    )

    logger.debug(f"Running blender from pytest-blender. CMD: {args}")
    try:
        with subprocess.Popen(args, stdout=sys.stdout, stderr=sys.stderr) as proc:

            def handled_exit():
                # hide "Exit:" message shown by pytest on exit
                sys.stderr = io.StringIO()
                pytest.exit(" ", returncode=proc.returncode)

            def on_sigint(signum, frame):
                proc.send_signal(signum)
                handled_exit()

            signal.signal(signal.SIGINT, on_sigint)
            signal.signal(signal.SIGHUP, on_sigint)
            signal.signal(signal.SIGTERM, on_sigint)
            proc.communicate()

            handled_exit()
    except FileNotFoundError:
        sys.stderr.write(f"Blender executable '{blender_executable}' not found!\n")
        raise SystemExit(1)
