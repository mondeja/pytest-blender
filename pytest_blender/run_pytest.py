"""Script ran by ``plugin.py`` module using a builtin Blender Python interpreter.

Keep in mind that may be some functions here that, although are used in other
parts of the package like ``get_blender_binary_path_python``, can't be located
outside this module because the installation of `pytest-blender` in the Blender
builtin Python intepreter shouldn't be mandatory, so avoid
``from pytest_blender...`` imports in this module.
"""

import os
import shlex
import subprocess
import sys

import pytest


def _join(value):
    try:
        from shlex import join
    except ImportError:
        return " ".join(value)
    else:
        return join(value)


# this function can't be in 'utils'
def get_blender_binary_path_python(blender_executable):
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
    stdout = subprocess.check_output(
        [
            blender_executable,
            "-b",
            "--python-expr",
            "import bpy;print(bpy.app.binary_path_python)",
        ]
    )

    blender_python_path = None
    for line in stdout.decode("utf-8").splitlines():
        if line.startswith(os.sep) and os.path.exists(line):
            blender_python_path = line
            break
    return blender_python_path


def main():
    raw_argv = shlex.split(_join(sys.argv).split(" -- ")[1:][0])

    # disable self-propagation, if installed in Blender Python interpreter
    argv = ["-p", "no:pytest-blender"]

    # parse Blender executable location, propagated from hook
    blender_executable, _inside_bexec_arg = (None, None)
    for arg in raw_argv:
        if arg == "--pytest-blender-executable":
            _inside_bexec_arg = True
            continue
        elif _inside_bexec_arg:
            blender_executable = arg
            _inside_bexec_arg = False
            continue
        argv.append(arg)

    class PytestBlenderPlugin:
        """Pytest plugin used by pytest-blender.

        Injects all the fixtures in the Blender's PyTest session of the user.
        """

        def _blender_python_executable(self, request):
            blender_python_executable = None

            # if pytest is executed without cache provider, the 'cache'
            #   attribute will not be available (-p no:cacheprovider)
            if hasattr(request.config, "cache"):
                blender_python_executable = request.config.cache.get(
                    "pytest-blender/blender-python-executable",
                    None,
                )

            if blender_python_executable is None:
                blender_python_executable = get_blender_binary_path_python(
                    blender_executable,
                )
                if hasattr(request.config, "cache"):
                    request.config.cache.set(
                        "pytest-blender/blender-python-executable",
                        blender_python_executable,
                    )
            return blender_python_executable

        @pytest.fixture
        def blender_executable(self):
            """Get the executable of the current Blender's session."""
            return blender_executable

        @pytest.fixture
        def blender_python_executable(self, request):
            """Get the executable of the current Blender's Python session."""
            return self._blender_python_executable(request)

        @pytest.fixture
        def blender_version(self, request):
            """Get the Blender version of the current session."""
            blender_version = None

            if hasattr(request.config, "cache"):
                blender_version = request.config.cache.get(
                    "pytest-blender/blender-version",
                    None,
                )

            if blender_version is None:
                version_stdout = subprocess.check_output(
                    [blender_executable, "--version"]
                )
                blender_version = (
                    version_stdout.decode("utf-8").splitlines()[0].split(" ")[1]
                )
                if hasattr(request.config, "cache"):
                    request.config.cache.set(
                        "pytest-blender/blender-version",
                        blender_version,
                    )
            return blender_version

        @pytest.fixture
        def blender_python_version(self, request):
            """Get the version of the Blender's Python executable."""
            blender_python_version = None

            if hasattr(request.config, "cache"):
                blender_python_version = request.config.cache.get(
                    "pytest-blender/blender-python-version",
                    None,
                )

            if blender_python_version is None:
                blender_python_executable = self._blender_python_executable(request)
                blender_python_version_stdout = subprocess.check_output(
                    [
                        blender_python_executable,
                        "--version",
                    ]
                )
                blender_python_version = (
                    blender_python_version_stdout.decode("utf-8")
                    .splitlines()[0]
                    .split(" ")[1]
                )
                if hasattr(request.config, "cache"):
                    request.config.cache.set(
                        "pytest-blender/blender-python-version",
                        blender_python_version,
                    )
            return blender_python_version

        @pytest.fixture(scope="session")
        def install_addons_from_dir(self, request):
            """Install Blender's addons from directory.

            Installs a set of Blender's addons into the current Blender's
            session specifying the names of the addons to be installed.
            """

            def _install_addons_from_dir(
                addons_dir,
                addon_module_names,
                save_userpref=True,
                default_set=True,
                persistent=True,
                **kwargs,
            ):
                import addon_utils  # noqa F401
                import bpy  # noqa F401

                for addon_module_name in addon_module_names:
                    addon_filepath = os.path.join(addons_dir, f"{addon_module_name}.py")
                    bpy.ops.preferences.addon_install(filepath=addon_filepath, **kwargs)
                    addon_utils.enable(
                        addon_module_name,
                        default_set=default_set,
                        persistent=persistent,
                    )
                if save_userpref:
                    bpy.ops.wm.save_userpref()

            return _install_addons_from_dir

        @pytest.fixture(scope="session")
        def disable_addons(self, request):
            """Disable installed addons in the current Blender's session."""

            def _disable_addons(
                addon_module_names,
                save_userpref=True,
                default_set=True,
                **kwargs,
            ):
                """Disables a set of addons by module name.

                Parameters
                ----------

                addon_module_names : list
                  Name of the addons modules (without the ``.py`` extension).

                save_userpref : bool
                  Save user preferences after disable.
                """
                import addon_utils  # noqa F401

                for addon_module_name in addon_module_names:
                    addon_utils.disable(
                        addon_module_name,
                        default_set=default_set,
                        **kwargs,
                    )
                if save_userpref:
                    import bpy  # noqa F401

                    bpy.ops.wm.save_userpref()

            return _disable_addons

    return pytest.main(argv, plugins=[PytestBlenderPlugin()])


if __name__ == "__main__":
    sys.exit(main())
