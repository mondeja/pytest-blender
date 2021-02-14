import shutil
import sys


def which_blender_by_os():
    if sys.platform == "darwin":
        return "Blender"
    return "blender.exe" if "win" in sys.platform else shutil.which("blender")
