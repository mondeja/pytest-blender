# pytest-blender

[![PyPI][pypi-version-badge-link]][pypi-link]
[![Python versions][pypi-pyversions-badge-link]][pypi-link]
[![License][license-image]][license-link]
[![Tests][tests-image]][tests-link]

Pytest plugin for Blender testing. Executes your pytest testsuite with
Blender in headless mode using its builtin Python interpreter.

## Install

```bash
pip install pytest-blender
```

## Documentation

### Usage

#### Install dependencies in Blender Python interpreter

Before execute it, you need to install your testing dependencies inside the
builtin Blender Python interpreter. To get the interpreter location you can
use the CLI utility `pytest-blender`, something like:

```bash
blender_python="$(pytest-blender)"
$blender_python -m ensurepip
$blender_python -m pip install -r test-requirements.txt
```

You can also get the intepreter for a custom Blender installation location
with `--blender-executable` option:

```bash
pytest-blender --blender-executable ~/blender-2.91.2-linux64/blender
```

#### Execute tests

After installing dependencies, just call pytest as usually.

```bash
pytest -svv
```

```
Blender 2.82 (sub 7)
Read prefs: ~/.config/blender/2.82/config/userpref.blend
========================= test session starts ==================================
platform linux -- Python 3.8.5, pytest-6.1.2, py-1.9.0, pluggy-0.13.1 -- /usr/bin/blender
cachedir: .pytest_cache
rootdir: /home/mondeja/files/code/pytest-blender
collected 1 item

tests/test_bpy_import.py::test_inside_blender <module 'bpy' from '/usr/share/blender/scripts/modules/bpy/__init__.py'>
PASSED
=========================== 1 passed in 0.01s ==================================
```

Just can specify a custom blender executable path using `--blender-executable`
option:

```bash
pytest --blender-executable ~/blender-2.91.2-linux64/blender
```

```
Blender 2.91.2 (hash 5be9ef417703 built 2021-01-19 16:16:34)
Read prefs: ~/.config/blender/2.91/config/userpref.blend
found bundled python: ~/blender-2.91.2-linux64/2.91/python
============================ test session starts ===============================
platform linux -- Python 3.7.7, pytest-6.2.2, py-1.10.0, pluggy-0.13.1
rootdir: ~/pytest-blender
collected 1 item

tests/test_bpy_import.py .                                                [100%]

============================== 1 passed in 0.00s ===============================
```

### Reference

#### Fixtures

<a name="blender_executable" href="#blender_executable">#</a> <b>blender_executable</b> ⇒ `str`

Returns the path of the executable that has started the current Blender session.

<a name="blender_version" href="#blender_version">#</a> <b>blender_version</b> ⇒ `str`

Returns the version of Blender running in the current session.

<a name="blender_python_executable" href="#blender_python_executable">#</a> <b>blender_python_executable</b> ⇒ `str`

Returns the path of the Python executable builtin in the Blender release of the
currently running session.

<a name="blender_python_version" href="#blender_python_version">#</a> <b>blender_python_version</b> ⇒ `str`

Returns the version of the Python executable builtin in the Blender release of
the currently running session.

<a name="install_addons_from_dir" href="#install_addons_from_dir">#</a> <b>install_addons_from_dir</b>(<i>addons_dir</i>, <i>addon_module_names</i>, <i>save_userpref=True</i>, <i>default_set=True</i>, <i>persistent=True</i>, <i>\*\*kwargs</i>)

Returns a function that installs and enables a set of addons whose modules are
located in a directory. This function is designed to be executed before the
pytest session to install the addons that you want to test, using the other
fixture [`disable_addons`](https://github.com/mondeja/pytest-blender#disable_addons)
to disable them after the execution of the suite:

```python
import os

ADDON_MODULE_NAMES = ["my_awesome_addon_module_name"]

@pytest.fixture(scope="session", autouse=True)
def _register_addons(request, install_addons_from_dir, disable_addons):
    install_addons_from_dir(os.path.abspath("src"), ADDON_MODULE_NAMES)
    yield
    disable_addons(ADDON_MODULE_NAMES)
```
- **addons_dir** (str) Directory in which are located the modules of the addons.
- **addon_module_names** (list) Name of the addons modules (without the `.py` extension).
- **save_userpref** (bool) Save user preferences after installation.
- **default_set** (bool) Set the user-preference calling `addon_utils.enable`.
- **persistent** (bool) Ensure the addon is enabled for the entire session
 (after loading new files).
- **\*\*kwargs** (dict) Subsecuent keyword arguments are passed to
 [`bpy.ops.preferences.addon_install`](https://docs.blender.org/api/current/bpy.ops.preferences.html#bpy.ops.preferences.addon_install).

<a name="disable_addons" href="#disable_addons">#</a> <b>disable_addons</b>(<i>addon_module_names</i>, <i>save_userpref=True</i>, <i>default_set=True</i>, <i>\*\*kwargs</i>)

Returns a function that disables a set of addons by module name. Is designed to
disables your addons after a pytest suite execution (check 
[`install_addons_from_dir`](https://github.com/mondeja/pytest-blender#install_addons_from_dir)
for an example).

- **addon_module_names** (list) Name of the addons modules (without the `.py` extension).
- **save_userpref** (bool) Save user preferences after installation.
- **default_set** (bool) Set the user-preference calling `addon_utils.disable`.
- **\*\*kwargs** (dict) Subsecuent keyword arguments are passed to `addon_utils.disable`.


[pypi-link]: https://pypi.org/project/pytest-blender
[pypi-version-badge-link]: https://img.shields.io/pypi/v/pytest-blender
[pypi-pyversions-badge-link]: https://img.shields.io/pypi/pyversions/pytest-blender
[license-image]: https://img.shields.io/pypi/l/pytest-blender?color=light-green
[license-link]: https://github.com/mondeja/pytest-blender/blob/master/LICENSE
[tests-image]: https://img.shields.io/github/workflow/status/mondeja/pytest-blender/CI
[tests-link]: https://github.com/mondeja/pytest-blender/actions?query=workflow%3ACI
