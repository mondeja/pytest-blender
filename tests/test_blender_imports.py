import pytest


try:
    from pytest_blender.test import pytest_blender_unactive
except ImportError:
    pytest_blender_unactive = False


@pytest.mark.skipif(
    pytest_blender_unactive,
    reason="Requires testing loading the pytest-blender plugin.",
)
def test_bpy_import():
    import bpy  # noqa F401


@pytest.mark.skipif(
    pytest_blender_unactive,
    reason="Requires testing loading the pytest-blender plugin.",
)
def test_addon_utils_import():
    import addon_utils  # noqa F401
