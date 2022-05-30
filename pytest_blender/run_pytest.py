"""Script ran by ``plugin.py`` module using a builtin Blender Python interpreter."""

import contextlib
import io
import os
import pprint
import shlex
import shutil
import subprocess
import sys
import tempfile
from importlib.machinery import SourceFileLoader

import pytest


PYTEST_BLENDER_ADDONS_DIR_TEMP = os.path.join(
    tempfile.gettempdir(),
    "pytest-blender-addons-dir",
)

# Import utilities using importlib machinery because pytest_blender is not
# installed inside Blender's Python interpreter
plugin_dir = os.path.abspath(os.path.dirname(__file__))
utils = SourceFileLoader(
    "pytest_blender.utils",
    os.path.join(plugin_dir, "utils.py"),
).load_module()

OPTIONS = (
    SourceFileLoader(
        "pytest_blender.options",
        os.path.join(plugin_dir, "options.py"),
    )
    .load_module()
    .OPTIONS
)


def removesuffix(value, suffix):
    return value[: -len(suffix)]


def get_addons_dir():
    # try with API
    try:
        import bpy

        blender_user_scripts = bpy.utils.script_path_user()
        if blender_user_scripts:
            return os.path.join(blender_user_scripts, "addons")
    except ImportError:
        pass

    # try with environment variable
    blender_user_scripts = os.environ.get("BLENDER_USER_SCRIPTS")
    if blender_user_scripts:
        return os.path.join(blender_user_scripts, "addons")

    # try dicovering from PATH
    response = None
    expected_enddir = os.path.join("scripts", "addons").rstrip(os.sep)

    # reversed because user's addons directory is added later to PATH
    for path in reversed(sys.path):
        if path.rstrip(os.sep).endswith(expected_enddir):
            response = path
            break

    if response is None:
        raise OSError(
            "Failed to obtain Blender's addons directory from"
            " PATH environment variable. Please, open a report in"
            " https://github.com/mondeja/pytest-blender/issues/new"
            f" including the next data:\n\nPlatform: {sys.platform}"
            f" - PATH: {pprint.pformat(sys.path)}"
        )

    return response


def _disable_addons(
    addons_ids,
    save_userpref=True,
    default_set=True,
    quiet=False,
    **kwargs,
):
    """Disables a set of addons by module names."""

    def _wrapper():
        import addon_utils  # noqa F401

        for addon_module_name in addons_ids:
            addon_utils.disable(
                addon_module_name,
                default_set=default_set,
                **kwargs,
            )
        if save_userpref:
            import bpy  # noqa F401

            bpy.ops.wm.save_userpref()

    if quiet:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            _wrapper()
    else:
        _wrapper()


def _install_addons_from_dir(
    addons_dir,
    addons_ids=None,
    save_userpref=True,
    default_set=True,
    persistent=True,
    quiet=False,
    **kwargs,
):
    def _wrapper():
        import addon_utils  # noqa F401
        import bpy  # noqa F401

        addons_to_zipify = []

        addons = []
        for filename in os.listdir(addons_dir):
            if filename == "__init__.py":
                continue  # exclude '__init__.py' from root

            filepath = os.path.join(addons_dir, filename)
            if filename.endswith(".py"):  # Python module addon
                addons.append(
                    [
                        removesuffix(filename, ".py"),
                        filepath,
                    ]
                )
            elif filename.endswith(".zip"):  # ZIP file addon
                addons.append(
                    [
                        removesuffix(filename, ".zip"),
                        filepath,  #
                    ]
                )
            elif (
                os.path.isdir(filepath)
                and addons_dir != PYTEST_BLENDER_ADDONS_DIR_TEMP
                and os.path.isfile(os.path.join(filepath, "__init__.py"))
            ):  # package adddon, must be converted to ZIP
                #
                # installation of packages is not supported by Blender if
                # they aren't zipped, so we zip the package into a temporal
                # directory and execute the `_install_addons_from_dir` function
                # against passing that directory
                addons_to_zipify.append(filename)

        if addons_ids:
            addons = list(filter(lambda a: a[0] in addons_ids, addons))
            addons_to_zipify = list(filter(lambda a: a in addons_ids, addons))

        # zipify addons packages and install them
        if addons_to_zipify:
            if not os.path.isdir(PYTEST_BLENDER_ADDONS_DIR_TEMP):
                os.mkdir(PYTEST_BLENDER_ADDONS_DIR_TEMP)

            for addon_name in addons_to_zipify:
                in_filepath = os.path.join(addons_dir, addon_name)
                out_filepath = utils.zipify_addon_package(
                    in_filepath, PYTEST_BLENDER_ADDONS_DIR_TEMP
                )
                addons.append([addon_name, out_filepath])

            _install_addons_from_dir(
                PYTEST_BLENDER_ADDONS_DIR_TEMP,
                save_userpref=save_userpref,
                default_set=default_set,
                persistent=persistent,
                quiet=quiet,
                **kwargs,
            )

        if not addons:
            raise ValueError("You need to pass at least one addon to install.")

        installed_addons_modnames = []
        addons_to_uninstall = []

        def skip_addon_installation(addon_module_name):
            sys.stdout.write(
                "[pytest-blender] Skipping installation of module"
                f" '{addon_module_name}' as is not a Blender addon"
                " (missing 'bl_info' module attribute)\n",
            )
            addons_to_uninstall.append(addon_module_name)

        for addon_module_name, addon_module_path in addons:
            try:
                bpy.ops.preferences.addon_install(filepath=addon_module_path, **kwargs)
                addon_utils.enable(
                    addon_module_name,
                    default_set=default_set,
                    persistent=persistent,
                )
            except AttributeError as exc:
                if f"module '{addon_module_name}' has no attribute 'bl_info'" in str(
                    exc
                ):
                    skip_addon_installation(addon_module_name)
                else:
                    raise
            except ModuleNotFoundError as exc:
                if f"No module named '{addon_module_name}'" in str(exc):
                    skip_addon_installation(addon_module_name)
                else:
                    raise
            else:
                installed_addons_modnames.append(addon_module_name)

        if addons_to_uninstall:
            # addons could be installed because the attribute error
            # for missing bl_info constants are raised in
            # `addon_utils.enable`, after installing them
            _uninstall_addons(addons_to_uninstall)

        if save_userpref:
            bpy.ops.wm.save_userpref()

        return installed_addons_modnames

    return _wrapper()


def _uninstall_addons(addons_ids, quiet=False, **kwargs):
    _disable_addons(addons_ids, quiet=quiet, **kwargs)
    addons_dir = get_addons_dir()

    for modname in addons_ids:
        modpath = os.path.join(addons_dir, modname)
        if os.path.isfile(f"{modpath}.py"):
            os.remove(f"{modpath}.py")
        if os.path.isdir(modpath) and os.path.isfile(
            os.path.join(modpath, "__init__.py")
        ):
            shutil.rmtree(modpath)


def main():
    raw_argv = shlex.split(utils.shlex_join(sys.argv).split(" -- ")[1:][0])

    # disable self-propagation, if installed in Blender Python interpreter
    argv = ["-p", "no:pytest-blender"]

    # TODO: parse blender-template?
    # TODO: add argument to debug invocation of Blender from pytest-blender

    # parse addons directories location
    _addons_dirs, _inside_addons_dir_arg = ([], None)

    # parse addons cleaning strategy for installed addons from directories
    _addons_cleaning, _inside_addons_cleaning_arg = ("uninstall", None)

    # parse Blender executable location, propagated from hook
    _blender_executable, _inside_bexec_arg = (None, None)
    for arg in raw_argv:
        if arg == "--pytest-blender-addons-dir":
            _inside_addons_dir_arg = True
            continue
        elif _inside_addons_dir_arg:
            _addons_dirs.append(arg)
            _inside_addons_dir_arg = False
            continue
        elif arg == "--pytest-blender-addons-cleaning":
            _inside_addons_cleaning_arg = True
            continue
        elif _inside_addons_cleaning_arg:
            _addons_cleaning = arg
            _inside_addons_cleaning_arg = False
            continue
        elif arg == "--pytest-blender-executable":
            _inside_bexec_arg = True
            continue
        elif _inside_bexec_arg:
            _blender_executable = arg
            _inside_bexec_arg = False
            continue

        argv.append(arg)

    class PytestBlenderPlugin:
        """Pytest plugin used by pytest-blender.

        Injects all the fixtures in the Blender's PyTest session of the user.
        """

        def _blender_python_executable(self, request):
            response = None

            # if pytest is executed without cache provider, the 'cache'
            #   attribute will not be available (-p no:cacheprovider)
            if hasattr(request.config, "cache"):
                response = request.config.cache.get(
                    "pytest-blender/blender-python-executable",
                    None,
                )

            if response is None:
                response = utils.get_blender_binary_path_python(
                    _blender_executable,
                    blend_version=self._blender_version(request),
                )
                if hasattr(request.config, "cache"):
                    request.config.cache.set(
                        "pytest-blender/blender-python-executable",
                        response,
                    )
            return response

        @pytest.fixture
        def blender_executable(self):
            """Get the executable of the current Blender's session."""
            return _blender_executable

        @pytest.fixture
        def blender_python_executable(self, request):
            """Get the executable of the current Blender's Python session."""
            return self._blender_python_executable(request)

        def _blender_version(self, request):
            response = None

            if hasattr(request.config, "cache"):
                response = request.config.cache.get(
                    "pytest-blender/blender-version",
                    None,
                )

            if response is None:
                response = utils.get_blender_version(_blender_executable)
                if hasattr(request.config, "cache"):
                    request.config.cache.set(
                        "pytest-blender/blender-version",
                        response,
                    )
            return response

        @pytest.fixture
        def blender_version(self, request):
            """Get the Blender version of the current session."""
            return self._blender_version(request)

        @pytest.fixture
        def blender_python_version(self, request):
            """Get the version of the Blender's Python executable."""
            response = None

            if hasattr(request.config, "cache"):
                response = request.config.cache.get(
                    "pytest-blender/blender-python-version",
                    None,
                )

            if response is None:
                blender_python_executable = self._blender_python_executable(request)
                blender_python_version_stdout = subprocess.check_output(
                    [
                        blender_python_executable,
                        "--version",
                    ]
                )
                response = (
                    blender_python_version_stdout.decode("utf-8")
                    .splitlines()[0]
                    .split(" ")[1]
                )
                if hasattr(request.config, "cache"):
                    request.config.cache.set(
                        "pytest-blender/blender-python-version",
                        response,
                    )
            return response

        @pytest.fixture(scope="session")
        def blender_addons_dir(self, request):
            """Get the path to the directory where addons are installed.

            See https://docs.blender.org/manual/en/latest/advanced/blender_directory_layout.html
            """  # noqa E501
            response = None

            if hasattr(request.config, "cache"):
                response = request.config.cache.get(
                    "pytest-blender/addons_dir",
                    None,
                )

            if response is None:
                response = get_addons_dir()
            return response

        @pytest.fixture(scope="session")
        def install_addons_from_dir(self):
            """Install Blender addons located into a directory."""
            return _install_addons_from_dir

        @pytest.fixture(scope="session")
        def disable_addons(self):
            """Disable installed addons in the current Blender's session.

            This does not includes deleting of data files from the Blender's
            addons directory.
            """
            return _disable_addons

        @pytest.fixture(scope="session")
        def uninstall_addons(self):
            """Removes the addons files from the Blender's addons directory."""
            return _uninstall_addons

        def pytest_addoption(self, parser):
            # avoid warnings about pytest-blender ini options not defined
            for option in OPTIONS:
                parser.addini(option, "")  # empty help, is irrelevant here

    run_pytest = lambda: pytest.main(argv, plugins=[PytestBlenderPlugin()])

    if not _addons_dirs:
        return run_pytest()

    addons_ids = []
    for addons_dir in _addons_dirs:
        addons_ids.extend(_install_addons_from_dir(addons_dir, quiet=True))

    exitcode = run_pytest()

    # follow chosen addons cleaning strategy
    if _addons_cleaning == "uninstall":
        _uninstall_addons(addons_ids, quiet=True)
    elif _addons_cleaning == "disable":
        _disable_addons(addons_ids, quiet=True)

    # remove zipyfied addons temporal dir
    if os.path.isdir(PYTEST_BLENDER_ADDONS_DIR_TEMP):
        shutil.rmtree(PYTEST_BLENDER_ADDONS_DIR_TEMP)
    return exitcode


if __name__ == "__main__":
    raise SystemExit(main())
