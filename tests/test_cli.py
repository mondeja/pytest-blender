import os
import subprocess

import pytest


try:
    from pytest_blender.test import pytest_blender_active
except ImportError:
    pytest_blender_active = True


@pytest.mark.skipif(
    pytest_blender_active,
    reason="Requires testing without loading the pytest-blender plugin.",
)
def test_pytest_blender_cli():
    output = subprocess.check_output(
        ["pytest-blender"],
        stderr=subprocess.STDOUT,
        shell=True,
    ).decode("utf-8")

    assert output.count("\n") == 1
    assert output.split(os.sep)[-1].startswith("python")
    assert os.path.isfile(output.rstrip("\n"))
