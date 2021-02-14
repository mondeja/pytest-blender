import shlex
import sys

import pytest


def _join(value):
    try:
        from shlex import join
    except ImportError:
        return " ".join(value)
    else:
        return join(value)


if __name__ == "__main__":
    argv = shlex.split(_join(sys.argv).split(" -- ")[1:][0])
    sys.exit(pytest.main(argv))
