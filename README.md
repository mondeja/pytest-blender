# pytest-blender

[![PyPI][pypi-version-badge-link]][pypi-link]
[![Python versions][pypi-pyversions-badge-link]][pypi-link]
[![License][license-image]][license-link]
[![Tests][tests-image]][tests-link]
[![Downloads][pypi-downloads-image]][pypi-downloads-link]

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

You can specify a custom blender executable path using `--blender-executable`
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

#### Arguments propagation

When you call `pytest`, all options like `--blender-executable` are passed
to the `pytest` suite running `pytest-blender`. If you want to pass arguments
to `blender` in its headless execution, add a `--` between `pytest` and
`blender` arguments. If you want to pass arguments to the `python` Blender's
interpreter, you need to add another `--` between arguments in a third group.

For example:

```sh
pytest -svv --blender-executable ~/blender -- --enable-event-simulate -- -b
```

In case that you don't want to pass arguments to `blender` but yes to `python`,
use double arguments group separation (`-- --`):

```sh
pytest -svv -- -- -b
```

#### Load startup template

You can use the `--blender-template` argument to pass a custom startup file:

```sh
pytest -svv --blender-template ~/.config/blender/2.93/config/startup.blend
```

#### Enable logging

Sometimes is useful to print debugging messages from `pytest_blender`.
You can enable logging in your `conftest.py` file by the next way:

```python
import logging

pytest_blender_logger = logging.getLogger("pytest_blender")
pytest_blender_logger.setLevel(logging.DEBUG)
pytest_blender_logger.addHandler(logging.StreamHandler())
```

### Reference

#### Fixtures

<a name="blender_executable" href="#blender_executable">#</a>
<b>blender_executable</b> ⇒ `str`

Returns the path of the executable that has started the current Blender
session.

<a name="blender_version" href="#blender_version">#</a> <b>blender_version</b>
⇒ `str`

Returns the version of Blender running in the current session.

<a name="blender_python_executable" href="#blender_python_executable">#</a>
<b>blender_python_executable</b> ⇒ `str`

Returns the path of the Python executable builtin in the Blender release of the
currently running session.

<a name="blender_python_version" href="#blender_python_version">#</a>
<b>blender_python_version</b> ⇒ `str`

Returns the version of the Python executable builtin in the Blender release of
the currently running session.

<a name="install_addons_from_dir" href="#install_addons_from_dir">#</a>
<b>install_addons_from_dir</b>(<i>addons_dir</i>,
<i>addon_module_names=None</i>, <i>recursive=False</i>,
<i>save_userpref=True</i>, <i>default_set=True</i>, <i>persistent=True</i>,
<i>\*\*kwargs</i>) ⇒ `list`

Function that installs and enables a set of addons whose modules are located in
a directory. This function is designed to be executed before the pytest session
to install the addons that you want to test, using the other fixture
[`disable_addons`](https://github.com/mondeja/pytest-blender#disable_addons)
to disable them after the execution of the test suite:

```python
import os

import pytest

@pytest.fixture(scope="session", autouse=True)
def _register_addons(request, install_addons_from_dir, disable_addons):
    addon_module_names = install_addons_from_dir(os.path.abspath("src"))
    yield
    disable_addons(addon_module_names)
```
- **addons_dir** (str) Directory in which are located the modules of the
 addons.
- **addon_module_names** (list) Name of the addons modules. If not defined
 (default) these will be discovered searching for addons in `addons_dir`
 directory. By default the discovering is not recursive through subdirectories,
 but you can enable it using the `recursive` argument.
- **recursive** (bool) If `addon_module_names` is not defined, the discovering
 of addons inside `addons_dir` is done recursively through subdirectories.
- **save_userpref** (bool) Save user preferences after installation.
- **default_set** (bool) Set the user-preference calling `addon_utils.enable`.
- **persistent** (bool) Ensure the addon is enabled for the entire session
 (after loading new files).
- **\*\*kwargs** (dict) Subsecuent keyword arguments are passed to
 [`bpy.ops.preferences.addon_install`](https://docs.blender.org/api/current/bpy.ops.preferences.html#bpy.ops.preferences.addon_install).

Returns the addon module names as a list, ready to be passed to
[`disable_addons`](https://github.com/mondeja/pytest-blender#disable_addons)
function.

<a name="disable_addons" href="#disable_addons">#</a>
<b>disable_addons</b>(<i>addon_module_names</i>, <i>save_userpref=True</i>,
<i>default_set=True</i>, <i>\*\*kwargs</i>)

Function that disables a set of addons by module name. Is designed to disable
your addons after a pytest suite execution (check 
[`install_addons_from_dir`](https://github.com/mondeja/pytest-blender#install_addons_from_dir)
for an example).

- **addon_module_names** (list) Name of the addons modules (without the `.py`
 extension).
- **save_userpref** (bool) Save user preferences after installation.
- **default_set** (bool) Set the user-preference calling `addon_utils.disable`.
- **\*\*kwargs** (dict) Subsecuent keyword arguments are passed to 
 `addon_utils.disable`.

### CI integration

You can use [blender-downloader][blender-downloader-link] to download multiple
versions of Blender in your CI and test against them. There is an example for
Github Actions in the CI configuration of this repository:

```yaml
jobs:
  test:
    name: Test
    runs-on: ${{ matrix.platform }}
    strategy:
      matrix:
        platform:
          - ubuntu-latest
          - macos-latest
        blender-version:
          - '2.90.1'
          - '2.83.9'
          - '2.82'
          - '2.81'
          - '2.80'
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python v3.8
        uses: actions/setup-python@v2
        with:
          python-version: 3.8
      - name: Upgrade PIP
        run: python -m pip install --upgrade pip
      - name: Cache Blender ${{ matrix.blender-version }}
        uses: actions/cache@v2.1.5
        id: cache-blender
        with:
          path: |
            blender-*
            _blender-executable-path.txt
          key: ${{ runner.os }}-${{ matrix.blender-version }}
      - name: Download Blender ${{ matrix.blender-version }}
        if: steps.cache-blender.outputs.cache-hit != 'true'
        id: download-blender
        run: |
          python -m pip install --upgrade blender-downloader
          echo "$(blender-downloader \
          ${{ matrix.blender-version }} --extract --remove-compressed \
          --quiet --print-blender-executable)" > _blender-executable-path.txt
      - name: Install dependencies
        id: install-dependencies
        run: |
          python -m pip install .[test]
          blender_executable="$(< _blender-executable-path.txt tr -d '\n')"
          python_blender_executable="$(pytest-blender --blender-executable $blender_executable)"
          $python_blender_executable -m ensurepip
          $python_blender_executable -m pip install pytest
          echo "::set-output name=blender-executable::$blender_executable"
      - name: Test with pytest
        run: pytest -svv --blender-executable "${{ steps.install-dependencies.outputs.blender-executable }}" tests
```

### Versions compatibility

- Latest version that officially supports Python3.6 is [v1.2.1]


[pypi-link]: https://pypi.org/project/pytest-blender
[pypi-version-badge-link]: https://img.shields.io/pypi/v/pytest-blender?logo=pypi&logoColor=white
[pypi-pyversions-badge-link]: https://img.shields.io/pypi/pyversions/pytest-blender?logo=python&logoColor=white
[license-image]: https://img.shields.io/pypi/l/pytest-blender?color=light-green&logo=freebsd&logoColor=white
[license-link]: https://github.com/mondeja/pytest-blender/blob/master/LICENSE
[tests-image]: https://img.shields.io/github/workflow/status/mondeja/pytest-blender/CI?logo=github&label=tests
[tests-link]: https://github.com/mondeja/pytest-blender/actions?query=workflow%3ACI
[pypi-downloads-image]: https://img.shields.io/pypi/dm/pytest-blender?logo=blender&logoColor=white
[pypi-downloads-link]: https://pypistats.org/packages/pytest-blender
[blender-downloader-link]: https://github.com/mondeja/blender-downloader
[v1.2.1]: https://github.com/mondeja/pytest-blender/releases/tag/v1.2.1
