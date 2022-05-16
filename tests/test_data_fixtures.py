"""pytest-blender fixtures tests."""

import pytest
from testing_utils import parametrize_plugin_on_off


parametrize_cache_args = pytest.mark.parametrize(
    "cache_args",
    (
        pytest.param([], id="cache_args=[]"),
        pytest.param(
            ["-p", "no:cacheprovider"], id='cache_args=["-p", "no:cacheprovider"]'
        ),
    ),
)


@parametrize_plugin_on_off
@parametrize_cache_args
def test_blender_executable(
    testing_context, plugin_args, cache_args, expected_exitcode
):
    with testing_context(
        {
            "tests/test_blender_executable.py": """
import os
import shutil

def test_blender_executable(blender_executable):
    assert blender_executable

    blender_executable_path = shutil.which(blender_executable)
    if not os.path.isfile(blender_executable_path):
        assert os.path.islink(blender_executable_path)
    else:
        assert os.path.isfile(blender_executable_path)
    assert "blender" in os.path.basename(blender_executable_path).lower()
"""
        }
    ) as ctx:
        _, stderr, exitcode = ctx.run([*plugin_args, *cache_args])
        assert exitcode == expected_exitcode, stderr


@parametrize_plugin_on_off
@parametrize_cache_args
def test_blender_python_executable(
    testing_context, plugin_args, cache_args, expected_exitcode
):
    with testing_context(
        {
            "tests/test_blender_python_executable.py": """
import os

def test_blender_python_executable(blender_python_executable):
    assert blender_python_executable
    if not os.path.isfile(blender_python_executable):
        assert os.path.islink(blender_python_executable)
    else:
        assert os.path.isfile(blender_python_executable)
    assert "python" in os.path.basename(blender_python_executable)
"""
        }
    ) as ctx:
        _, stderr, exitcode = ctx.run([*plugin_args, *cache_args])
        assert exitcode == expected_exitcode, stderr


@parametrize_plugin_on_off
@parametrize_cache_args
def test_blender_version(testing_context, plugin_args, cache_args, expected_exitcode):
    with testing_context(
        {
            "tests/test_blender_version.py": """
import re
import subprocess

def test_blender_version(blender_executable, blender_version):
    stdout = subprocess.check_output([blender_executable, "--version"])
    expected_blender_version = stdout.decode("utf-8").splitlines()[0].split(" ")[1]

    assert expected_blender_version == blender_version
    assert re.match(r"\\d+\\.\\d", blender_version)
"""
        }
    ) as ctx:
        _, stderr, exitcode = ctx.run([*plugin_args, *cache_args])
        assert exitcode == expected_exitcode, stderr


@parametrize_plugin_on_off
@parametrize_cache_args
def test_blender_python_version(
    testing_context, plugin_args, cache_args, expected_exitcode
):
    with testing_context(
        {
            "tests/test_blender_python_version.py": """
import re
import subprocess

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
    assert re.match(r"\\d+\\.\\d\\.?\\d*", blender_python_version)
"""
        }
    ) as ctx:
        _, stderr, exitcode = ctx.run([*plugin_args, *cache_args])
        assert exitcode == expected_exitcode, stderr


@parametrize_plugin_on_off
@parametrize_cache_args
def test_blender_addons_dir(
    testing_context, plugin_args, cache_args, expected_exitcode
):
    with testing_context(
        {
            "tests/test_blender_addons_dir.py": """
def test_blender_addons_dir(blender_addons_dir):
    assert 'scripts' in blender_addons_dir.lower()
    assert 'addons' in blender_addons_dir.lower()
"""
        }
    ) as ctx:
        _, stderr, exitcode = ctx.run([*plugin_args, *cache_args])
        assert exitcode == expected_exitcode, stderr
