from pytest_blender_zipped_from_dir.register import register, unregister  # noqa F401


bl_info = {
    "name": "Move X Axis",
    "category": "Object",
}


if __name__ == "__main__":
    register()
