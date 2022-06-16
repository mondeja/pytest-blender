import os
import pprint
import shutil
import subprocess
import sys
import zipfile


PYTEST_BLENDER_NEW_ISSUE_URL = (
    "https://github.com/mondeja/pytest-blender/issues/new/choose"
)
ZIP_ROOTS_IGNORE = [".DStore", ".git", ".gitignore", "__pycache__"]


class PytestBlenderException(Exception):
    pass


class GetPythonBlenderPathError(PytestBlenderException):
    pass


def zipify_addon_package(in_dirpath, out_dirpath):
    zipped_path = os.path.join(
        out_dirpath,
        f"{os.path.basename(in_dirpath)}.zip",
    )

    with zipfile.ZipFile(zipped_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(in_dirpath):
            if os.path.basename(root) in ZIP_ROOTS_IGNORE:
                continue
            for file in files:
                filepath = os.path.join(root, file)
                zipf.write(
                    filepath,
                    os.path.relpath(
                        filepath,
                        os.path.join(in_dirpath, ".."),
                    ),
                )
    return zipped_path


def which_blender():
    """Get the expected Blender executable location by operative system."""
    _blender_executable = os.environ.get("BLENDER_EXECUTABLE")
    if _blender_executable is not None:
        return _blender_executable

    return (
        shutil.which("Blender")
        if sys.platform == "darwin"
        else ("blender.exe" if "win" in sys.platform else shutil.which("blender"))
    )


def parse_version(version_string):
    return tuple(int(i) for i in version_string.split(".") if i.isdigit())


def get_blender_version(blender_executable):
    """Get Blender's version goving its executable location.

    blender_executable : str
      Blender's executable location.

    Returns
    -------

    str: Blender's version.
    """
    version_stdout = subprocess.check_output([blender_executable, "--version"])
    return version_stdout.decode("utf-8").splitlines()[0].split(" ")[1]


def get_blender_binary_path_python(blender_executable, blend_version=None):
    """Get Blender's Python executable location.

    This function can't be in utils because the module is not loaded from
    Blender (current script is executed inside Blender's Python executable).

    Parameters
    ----------

    blender_executable : str
      Blender's executable location.

    Returns
    -------

    str: Blender's Python executable path.
    """
    if blend_version is None:
        blend_version = get_blender_version(blender_executable)
    id_string = "BLENDER-PYTHON-PATH:"
    python_expr = (
        f"import sys;print('{id_string}',sys.executable);"
        if parse_version(blend_version) >= (2, 91)
        else f"import bpy;print('{id_string}',bpy.app.binary_path_python)"
    )

    stdout = subprocess.check_output(
        [
            blender_executable,
            "-b",
            "--python-expr",
            python_expr,
        ],
        stderr=subprocess.STDOUT,
    )

    blender_python_path = None
    for line in stdout.decode("utf-8").splitlines():
        if line.startswith(id_string):
            blender_python_path = line.split(" ", maxsplit=1)[1]
            break
    if blender_python_path is None:
        debugging_data = {
            "platform": sys.platform,
            "blender_executable": blender_executable,
            "stdout": stdout,
        }
        raise GetPythonBlenderPathError(
            "Failed to retrieve the Blender's Python interpreter path."
            f" Please, submit a report at {PYTEST_BLENDER_NEW_ISSUE_URL}"
            f" including the next data:\n{pprint.pformat(debugging_data)}"
        )
    return blender_python_path


def get_addons_dir(blender_executable):
    stdout = subprocess.check_output(
        [
            blender_executable,
            "-b",
            "--python-expr",
            "import bpy;print(bpy.utils.script_path_user())",
        ],
        stderr=subprocess.STDOUT,
    )

    scripts_dir = None
    for line in stdout.decode("utf-8").splitlines():
        if line.endswith("scripts"):
            scripts_dir = line
            break
    return os.path.join(scripts_dir, "addons")


def shlex_join(value):
    try:
        from shlex import join
    except ImportError:
        return " ".join(value)
    else:
        return join(value)
