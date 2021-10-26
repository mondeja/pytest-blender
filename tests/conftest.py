"""pytest-blender tests configuration."""

import io
import os
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
        addon_module_names = ["pytest_blender_basic"]

        f = io.StringIO()
        with redirect_stdout(f):
            install_addons_from_dir(addons_dir, addon_module_names)

            yield

            disable_addons(addon_module_names)
