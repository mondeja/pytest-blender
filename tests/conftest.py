"""pytest-blender tests configuration."""

import io
import os
from contextlib import redirect_stdout

import pytest


@pytest.fixture(scope="session", autouse=True)
def _register_addon(request):
    import addon_utils
    import bpy

    addons_dir = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        "addons",
    )

    addons_module_names = ["pytest_blender_basic"]

    f = io.StringIO()
    with redirect_stdout(f):
        for addon_module_name in addons_module_names:
            addon_filepath = os.path.join(addons_dir, f"{addon_module_name}.py")
            bpy.ops.preferences.addon_install(filepath=addon_filepath, overwrite=True)
            addon_utils.enable(addon_module_name, default_set=True, persistent=True)
        bpy.ops.wm.save_userpref()

        yield

        for addon_module_name in addons_module_names:
            addon_utils.disable(addon_module_name, default_set=True)
        bpy.ops.wm.save_userpref()
