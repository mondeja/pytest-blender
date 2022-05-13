import bpy
from pytest_blender_zipped_from_dir.operator import (
    PytestBlenderZippedFromDirObjectMoveX,
)


def register():
    bpy.utils.register_class(PytestBlenderZippedFromDirObjectMoveX)


def unregister():
    bpy.utils.unregister_class(PytestBlenderZippedFromDirObjectMoveX)
