"""pytest-blender fixtures tests."""

import os
import re
import subprocess


def test_blender_executable(blender_executable):
    assert os.path.isfile(blender_executable)
    assert "blender" in os.path.basename(blender_executable).lower()


def test_blender_python_executable(blender_python_executable):
    assert os.path.isfile(blender_python_executable)
    assert "python" in os.path.basename(blender_python_executable)


def test_blender_version(blender_executable, blender_version):
    stdout = subprocess.check_output([blender_executable, "--version"])
    expected_blender_version = stdout.decode("utf-8").splitlines()[0].split(" ")[1]

    assert expected_blender_version == blender_version
    assert re.match(r"\d+\.\d", blender_version)


def test_blender_python_version(blender_python_version, blender_python_executable):
    blender_python_version_stdout = subprocess.check_output(
        [
            blender_python_executable,
            "--version",
        ]
    )
    expected_blender_python_version = (
        blender_python_version_stdout.decode("utf-8").splitlines()[0].split(" ")[1]
    )

    assert blender_python_version == expected_blender_python_version
    assert re.match(r"\d+\.\d\.?\d*", blender_python_version)
