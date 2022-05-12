"""Example addons testing."""

import pytest


try:
    from pytest_blender.test import pytest_blender_unactive
except ImportError:
    pytest_blender_unactive = False


@pytest.mark.skipif(
    pytest_blender_unactive,
    reason="Requires testing loading the pytest-blender plugin.",
)
def test_basic_addon():
    import addon_utils
    import bpy

    installed_addons = [addon.__name__ for addon in addon_utils.modules()]
    assert "pytest_blender_basic" in installed_addons
    assert "__init__" not in installed_addons

    operator_classes = [cls.__name__ for cls in bpy.types.Operator.__subclasses__()]
    assert "PytestBlenderBasicObjectMoveX" in operator_classes


@pytest.mark.skipif(
    pytest_blender_unactive,
    reason="Requires testing loading the pytest-blender plugin.",
)
def test_zipped_addon():
    import addon_utils
    import bpy

    installed_addons = [addon.__name__ for addon in addon_utils.modules()]
    assert "pytest_blender_zipped" in installed_addons

    operator_classes = [cls.__name__ for cls in bpy.types.Operator.__subclasses__()]
    assert "PytestBlenderZippedObjectMoveX" in operator_classes
