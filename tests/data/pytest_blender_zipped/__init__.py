from pytest_blender_zipped.register import register, unregister  # noqa F401


bl_info = {
    "name": "Move X Axis",
    "category": "Object",
}


if __name__ == "__main__":
    register()
