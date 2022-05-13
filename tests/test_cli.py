import os
import subprocess
import sys

import pytest


@pytest.mark.skipif(
    not os.environ.get("BLENDER_EXECUTABLE"),
    reason="The environment variable BLENDER_EXECUTABLE must be set to run this test",
)
def test_pytest_blender_cli():
    proc = subprocess.run(
        [
            sys.executable,
            os.path.join("pytest_blender", "__main__.py"),
            "--blender-executable",
            os.environ["BLENDER_EXECUTABLE"],
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert proc.stderr == b""

    stdout = proc.stdout.decode("utf-8")
    assert stdout.count("\n") == 1
    assert stdout.endswith("\n")
    assert stdout.split(os.sep)[-1].startswith("python")
    assert os.path.isfile(stdout.rstrip("\n"))
