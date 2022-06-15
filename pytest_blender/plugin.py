"""pytest-blender plugin"""

import io
import os
import signal
import subprocess
import sys

import pytest

from pytest_blender import utils
from pytest_blender.options import OPTIONS


def get_blender_executable(config):
    # from CLI
    blender_executable = config.getoption("--blender-executable")
    if blender_executable is not None:
        return blender_executable

    # from inicfg
    if "blender-executable" in config.inicfg:
        return config.inicfg["blender-executable"]

    # discover from system
    return utils.which_blender()


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
        return value

    addons_cleaning_strategy = config.getoption("--blender-addons-cleaning")
    if addons_cleaning_strategy:
        return addons_cleaning_strategy

    return OPTIONS["blender-addons-cleaning"]["opts"]["default"]


def add_template_arg(config, args):
    template = config.getoption("--blender-template")
    if template:
        args.append(os.path.abspath(os.path.expanduser(template)))
    elif "blender-template" in config.inicfg:
        args.append(
            os.path.abspath(os.path.expanduser(config.inicfg["blender-template"]))
        )


def get_pytest_blender_debug(config):
    return "pytest-blender-debug" in config.inicfg or config.getoption(
        "--pytest-blender-debug"
    )


@pytest.hookimpl(tryfirst=True)
def pytest_addoption(parser):
    for arg, argdef in OPTIONS.items():
        kwargs = argdef["opts"] if "opts" in argdef else {"default": None}
        parser.addoption(f"--{arg}", help=argdef["help"], **kwargs)
        parser.addini(arg, argdef["help"])


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    # execute with debugging capabilities?
    pytest_blender_debug = get_pytest_blender_debug(config)

    # build propagated CLI args
    args_groups, args_group_index = ([], [], []), 0
    argv = sys.argv[1:]
    i = 0
    options_cli_args = [f"--{arg}" for arg in OPTIONS.keys()]

    argv_length = len(argv)
    while i < argv_length:
        arg = argv[i]
        if arg in options_cli_args:
            i += 2
            continue
        elif arg in ["-h", "--help"]:
            return  # pytest's help, abort
        elif arg == "--":
            args_group_index += 1
            i += 1
            continue
        elif arg == "-p" and i < argv_length - 1 and argv[i + 1] == "pytest-blender":
            # the user is enabling the plugin explicitly, but we shouldn't
            # pass this enabling option to the Blender execution
            i += 2
            continue

        args_groups[args_group_index].append(arg)
        i += 1

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
            *addons_dirs_args,
            *addons_cleaning_strategy_args,
            *pytest_opts,  # propagate Pytest command line arguments
        ]
    )

    if pytest_blender_debug:
        sys.stdout.write(
            "[DEBUG (pytest-blender)] Running blender with:"
            f" {utils.shlex_join(args)}\n"
        )

    with subprocess.Popen(
        args, stdout=sys.stdout, stderr=sys.stderr, env=os.environ
    ) as proc:

        def handled_exit():
            # hide "Exit:" message shown by pytest on exit
            sys.stderr = io.StringIO()
            pytest.exit(" ", returncode=proc.returncode)

        def on_sigint(signum, frame):
            proc.send_signal(signum)
            handled_exit()

        signal.signal(signal.SIGINT, on_sigint)
        if "win" not in sys.platform:
            signal.signal(signal.SIGHUP, on_sigint)
        signal.signal(signal.SIGTERM, on_sigint)
        proc.communicate()

        handled_exit()
