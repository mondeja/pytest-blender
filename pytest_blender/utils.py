import shutil
import sys


def which_blender_by_os():
    """Get the expected Blender executable location by operative system."""
    if sys.platform == "darwin":
        return "Blender"
    return "blender.exe" if "win" in sys.platform else shutil.which("blender")
