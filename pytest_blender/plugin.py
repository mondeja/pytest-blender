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
        "help": "Directory with addons to install before test suite execution.",
        "opts": {"nargs": "+", "default": []},
    },
    "blender-addons-cleaning": {
        "help": (
            "What to do with addons installed after test suite execution."
            " It accepts one of the next strings: 'uninstall' (default,"
            " remove addons from Blender's user repository after testing),"
            " 'disable' (just disable the addons in Blender preferences)"
            " or 'keep' (keep the addons installed after testing, useful"
            " for manual reviews)."
        ),
        "opts": {"default": "uninstall", "choices": ["uninstall", "disable", "keep"]},
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


def get_addons_cleaning_strategy(config):
    addons_cleaning_strategy = config.getoption("--blender-addons-cleaning")
    if addons_cleaning_strategy:
        return addons_cleaning_strategy

    addons_cleaning_strategy = OPTIONS["blender-addons-cleaning"]["opts"]["default"]
    value = config.inicfg.get("blender-addons-cleaning")
    if value:
        choices = OPTIONS["blender-addons-cleaning"]["opts"]["choices"]
        rel_inipath = os.path.relpath(config.inipath, os.getcwd())
        if value not in choices:
            raise ValueError(
                f"The configuration for blender-addons-cleaning option '{value}'"
                f" defined inside {rel_inipath} must have one of the"
                f" next values: {', '.join(choices)}"
            )
        addons_cleaning_strategy = value
    return addons_cleaning_strategy


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
    pytest_help_opt = False

    # build propagated CLI args
    args_groups, args_group_index = ([], [], []), 0
    argv = sys.argv[1:]
    i = 0
    options_cli_args = [f"--{arg}" for arg in OPTIONS.keys()]
    while i < len(argv):
        arg = argv[i]
        if arg in options_cli_args:
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
    addons_dirs = get_addons_dir(config)
    if addons_dirs:
        for addons_dir in addons_dirs:
            addons_dirs_args.extend(["--pytest-blender-addons-dir", addons_dir])

        # installed addons cleaning strategy
        addons_cleaning_strategy_args = [
            "--pytest-blender-addons-cleaning",
            get_addons_cleaning_strategy(config),
        ]
    else:
        addons_cleaning_strategy_args = []

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
            *addons_cleaning_strategy_args,
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
