import os
import tempfile
import time


def test_sleep():
    pidfile = os.path.join(
        tempfile.gettempdir(), "pytest-blender-integration-sigint.pid"
    )
    with open(pidfile, "w") as f:
        f.write(str(os.getpid()))

    time.sleep(13)
