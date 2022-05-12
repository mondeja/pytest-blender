import bpy
from pytest_blender_zipped.operator import PytestBlenderZippedObjectMoveX


def register():
    bpy.utils.register_class(PytestBlenderZippedObjectMoveX)


def unregister():
    bpy.utils.unregister_class(PytestBlenderZippedObjectMoveX)
