"""Example addons testing."""

import _bpy
import addon_utils


def test_basic_addon():
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
