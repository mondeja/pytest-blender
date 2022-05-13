import os
import sys
import time

import pytest


@pytest.mark.skipif(
    not os.environ.get("hola"),
    reason="The environment variable SIGINT_PIDFILE must be set to run this test",
)
def test_sleep():
    with open(os.environ["SIGINT_PIDFILE"], "w") as f:
        f.write(str(os.getpid()))

    sys.stdout.write("DEBUG: BEFORE SLEEP\n")
    time.sleep(13)
    sys.stdout.write("DEBUG: AFTER SLEEP\n")
