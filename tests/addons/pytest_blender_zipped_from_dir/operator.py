import bpy


class PytestBlenderZippedFromDirObjectMoveX(bpy.types.Operator):
    """My Object Moving Script"""

    bl_idname = "object.move_x_zipped_from_dir"
    bl_label = "Move X by One"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        scene = context.scene
        for obj in scene.objects:
            obj.location.x += 1.0

        return {"FINISHED"}
