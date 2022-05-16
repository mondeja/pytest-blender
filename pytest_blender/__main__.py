import argparse
import sys

from pytest_blender import __version__
from pytest_blender.utils import get_blender_binary_path_python, which_blender


__description__ = "Show a Blender's builtin Python interpreter location."


def build_parser():
    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="%(prog)s " + __version__,
        help="Show program version number and exit.",
    )
    parser.add_argument(
        "--blender-executable",
        dest="blender_executable",
        nargs=1,
        default=which_blender,
        help="Custom Blender executable location for 'pytest-blender' plugin.",
    )
    return parser


def parse_args(args):
    parser = build_parser()
    if "-h" in args or "--help" in args:
        parser.print_help()
        sys.exit(0)
    opts = parser.parse_args(args)

    if hasattr(opts.blender_executable, "__call__"):
        opts.blender_executable = opts.blender_executable()
    else:
        opts.blender_executable = opts.blender_executable[0]

    return opts


def run(args):
    opts = parse_args(args)
    blender_python = get_blender_binary_path_python(opts.blender_executable)
    sys.stdout.write(f"{blender_python}\n")

    return 0


def main():
    sys.exit(run(args=sys.argv[1:]))


if __name__ == "__main__":
    main()
