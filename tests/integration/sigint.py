import os
import sys
import tempfile
import time


def test_sleep():
    pidfile = os.path.join(
        tempfile.gettempdir(), "pytest-blender-integration-sigint.pid"
    )
    with open(pidfile, "w") as f:
        f.write(str(os.getpid()))

    sys.stdout.write("DEBUG: BEFORE SLEEP\n")
    time.sleep(13)
    sys.stdout.write("DEBUG: AFTER SLEEP\n")
