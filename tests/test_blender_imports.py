import pytest


@pytest.mark.blender
def test_bpy_import():
    import bpy  # noqa F401


@pytest.mark.blender
def test_addon_utils_import():
    import addon_utils  # noqa F401
