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
    import _bpy
    import addon_utils

    _module_loaded = False
    for addon_module in addon_utils.modules():
        if addon_module.__name__ == "pytest_blender_basic":
            _module_loaded = True
    assert _module_loaded

    _operator_class_loaded = False
    for operator_cls in _bpy.types.Operator.__subclasses__():
        if operator_cls.__name__ == "ObjectMoveX":
            _operator_class_loaded = True
    assert _operator_class_loaded
