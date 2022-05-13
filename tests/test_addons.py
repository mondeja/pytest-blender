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
@pytest.mark.parametrize(
    ("addon_name", "expected_operator_class"),
    (
        [
            ("pytest_blender_basic", "PytestBlenderBasicObjectMoveX"),
            ("pytest_blender_zipped", "PytestBlenderZippedObjectMoveX"),
            ("pytest_blender_zipped_from_dir", "PytestBlenderZippedFromDirObjectMoveX"),
        ]
    ),
)
def test_addons(addon_name, expected_operator_class):
    import addon_utils
    import bpy

    installed_addons = [addon.__name__ for addon in addon_utils.modules()]
    assert addon_name in installed_addons
    assert "__init__" not in installed_addons

    operator_classes = [cls.__name__ for cls in bpy.types.Operator.__subclasses__()]
    assert expected_operator_class in operator_classes
