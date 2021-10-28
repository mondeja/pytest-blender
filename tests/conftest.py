"""pytest-blender tests configuration."""

import io
import os
import sys
from contextlib import redirect_stdout

import pytest


try:
    from pytest_blender.test import pytest_blender_active
except ImportError:
    # executing pytest from Python Blender executable, the plugin is active
    pytest_blender_active = True

if pytest_blender_active:

    @pytest.fixture(scope="session", autouse=True)
    def _register_addons(request, install_addons_from_dir, disable_addons):
        addons_dir = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            "addons",
        )

        f = io.StringIO()
        with redirect_stdout(f):
            addon_module_names = install_addons_from_dir(addons_dir)
        yield
        sys.stdout.write("\n")
        with redirect_stdout(f):
            disable_addons(addon_module_names)


else:
    pytest_plugins = "pytester"
