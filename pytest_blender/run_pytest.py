"""Script ran by ``plugin.py`` module using a builtin Blender Python interpreter.

Keep in mind that may be some functions here that, although are used in other
parts of the package like ``get_blender_binary_path_python``, can't be located
outside this module because the installation of `pytest-blender` in the Blender
builtin Python intepreter shouldn't be mandatory, so avoid
``from pytest_blender...`` imports in this module.
"""

import os
import shlex
import subprocess
import sys

import pytest


def _join(value):
    try:
        from shlex import join
    except ImportError:
        return " ".join(value)
    else:
        return join(value)


# this function can't be in 'utils'
def get_blender_binary_path_python(blender_executable):
    stdout = subprocess.check_output(
        [
            blender_executable,
            "-b",
            "--python-expr",
            "import bpy;print(bpy.app.binary_path_python)",
        ]
    )

    blender_python_path = None
    for line in stdout.decode("utf-8").splitlines():
        if line.startswith(os.sep):
            blender_python_path = line
            break
    return blender_python_path


def main():
    raw_argv = shlex.split(_join(sys.argv).split(" -- ")[1:][0])

    # disable self-propagation, if installed in Blender Python interpreter
    argv = ["-p", "no:pytest-blender"]

    # parse Blender executable location, propagated from hook
    blender_executable, _inside_bexec_arg = (None, None)
    for arg in raw_argv:
        if arg == "--pytest-blender-executable":
            _inside_bexec_arg = True
            continue
        elif _inside_bexec_arg:
            blender_executable = arg
            _inside_bexec_arg = False
            continue
        argv.append(arg)

    class PytestBlenderPlugin:
        def _blender_python_executable(self, request):
            blender_python_executable = request.config.cache.get(
                "pytest-blender/blender-python-executable",
                None,
            )
            if blender_python_executable is None:
                blender_python_executable = get_blender_binary_path_python(
                    blender_executable,
                )
                request.config.cache.set(
                    "pytest-blender/blender-python-executable",
                    blender_python_executable,
                )
            return blender_python_executable

        @pytest.fixture
        def blender_executable(self):
            return blender_executable

        @pytest.fixture
        def blender_python_executable(self, request):
            return self._blender_python_executable(request)

        @pytest.fixture
        def blender_version(self, request):
            blender_version = request.config.cache.get(
                "pytest-blender/blender-version",
                None,
            )
            if blender_version is None:
                version_stdout = subprocess.check_output(
                    [blender_executable, "--version"]
                )
                blender_version = (
                    version_stdout.decode("utf-8").splitlines()[0].split(" ")[1]
                )
                request.config.cache.set(
                    "pytest-blender/blender-version",
                    blender_version,
                )
            return blender_version

        @pytest.fixture
        def blender_python_version(self, request):
            blender_python_version = request.config.cache.get(
                "pytest-blender/blender-python-version",
                None,
            )
            if blender_python_version is None:
                blender_python_executable = self._blender_python_executable(request)
                blender_python_version_stdout = subprocess.check_output(
                    [
                        blender_python_executable,
                        "--version",
                    ]
                )
                blender_python_version = (
                    blender_python_version_stdout.decode("utf-8")
                    .splitlines()[0]
                    .split(" ")[1]
                )
                request.config.cache.set(
                    "pytest-blender/blender-python-version",
                    blender_python_version,
                )
            return blender_python_version

    return pytest.main(argv, plugins=[PytestBlenderPlugin()])


if __name__ == "__main__":
    sys.exit(main())
