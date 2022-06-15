# pytest-blender

[![PyPI][pypi-version-badge-link]][pypi-link]
[![Python versions][pypi-pyversions-badge-link]][pypi-link]
[![License][license-image]][license-link]
[![Tests][tests-image]][tests-link]
[![Downloads][pypi-downloads-image]][pypi-downloads-link]

Pytest plugin for Blender testing. Executes your pytest testsuite with
Blender in headless mode using its builtin Python interpreter.

## Install

```sh
pip install pytest-blender
```

## Documentation

### Usage

Before execute it, you need to install your testing dependencies inside the
builtin Blender Python interpreter. To get the interpreter location you can
use the CLI utility `pytest-blender`, something like:

```sh
blender_python="$(pytest-blender)"
$blender_python -m ensurepip
$blender_python -m pip install -r test-requirements.txt
```

After installing dependencies, just call pytest as usually.

```sh
pytest -svv
```

```
Blender 2.82 (sub 7)
Read prefs: ~/.config/blender/2.82/config/userpref.blend
=================== test session starts ===================
platform linux -- Python 3.8.5, pytest-6.1.2, py-1.9.0, pluggy-0.13.1 -- /usr/bin/blender
cachedir: .pytest_cache
rootdir: /home/mondeja/files/code/pytest-blender
collected 1 item

tests/test_bpy_import.py::test_inside_blender <module 'bpy' from '/usr/share/blender/scripts/modules/bpy/__init__.py'>
PASSED
==================== 1 passed in 0.01s ====================
```

### Reference

#### Configuration

All options can be passed as a CLI argument like `--[option-name]` or
defined inside a [configuration file][pytest-configuration].

##### `blender-executable`

Specify a custom `blender` executable location.

```sh
pytest --blender-executable ~/blender-2.91.2-linux64/blender
```

```ini
[pytest]
blender-executable = ~/blender-2.91.2-linux64/blender
```

```
Blender 2.91.2 (hash 5be9ef417703 built 2021-01-19 16:16:34)
Read prefs: ~/.config/blender/2.91/config/userpref.blend
found bundled python: ~/blender-2.91.2-linux64/2.91/python
=================== test session starts ===================
platform linux -- Python 3.7.7, pytest-6.2.2, py-1.10.0, pluggy-0.13.1
rootdir: ~/pytest-blender
collected 1 item

tests/test_bpy_import.py .                                                [100%]

==================== 1 passed in 0.00s ====================
```

##### `blender-template`

Load a custom startup `.blend` template.

```sh
pytest -svv --blender-template ~/.config/blender/2.93/config/startup.blend
```

```ini
[pytest]
blender-template = ~/.config/blender/2.93/config/startup.blend
addopts = -svv
```

##### `blender-addons-dirs`

Install addons inside Blender before executing the test suite. This allows
you to easily test them.

By "addons" Blender understands Python scripts whose file names
end with `.py`, `.zip` files for compressed packages with multiple modules
or directories for Python packages which contain a `__init__.py` file.
These must be located in the root of each directory passed to
`blender-addons-dirs`.

For example, given the next directory tree:

```tree
📁 addons-dirs
├── 📁 private-addons
│   └── 📁 package_addon
│       ├── 📄 __init__.py 
│       └── 📄 main.py
|
└── 📁 public-addons
    ├── 📄 module_addon.py
    └── 📄 compressed_addon.zip
        ├── 📄 __init__.py 
        └── 📄 main.py
```

The next configurations will install the addons `package_addon`,
`module_addon` and `compressed_addon`.

```sh
pytest tests --blender-addons-dirs addons-dirs/private-addons addons-dirs/public-addons
```

```ini
[pytest]
blender-addons-dirs =
    addons-dirs/private-addons
    addons-dirs/public-addons
```

You can also define a unique addons directory in configuration files
defining it as a string:

```ini
[pytest]
blender-addons-dirs = addons-dirs/public-addons
```

If you need more complex setups see the fixtures
[`install_addons_from_dir`](#install_addons_from_dir),
[`disable_addons`](#disable_addons) and
[`uninstall_addons`](#uninstall_addons).

##### `blender-addons-cleaning`

Define the addons cleaning strategy to follow after executing your
test suite. It only affects to the addons installed using
[`blender-addons-dirs`](#blender-addons-dirs).

It accepts a string one of the next values:

- `uninstall` (default): Uninstall the addons after executing the
 test suite.
- `disable`: Just disable the addons in user preferences, but does
 not uninstall them.
- `keep`: Keep the addons enabled. Useful if you want to manually
 review the addons or while you're developing. 

```sh
pytest --blender-addons-cleaning disable
```

```ini
[pytest]
blender-addons-cleaning = disable
```

##### `pytest-blender-debug`

Show in STDOUT the command executed by pytest-blender executing your
test suite.

```sh
pytest --pytest-blender-debug
```

```ini
[pytest]
pytest-blender-debug = true
```

```
[DEBUG (pytest-blender)] Running blender with: /usr/bin/blender -b --python /home/foo/files/code/pytest-blender/pytest_blender/run_pytest.py -- --pytest-blender-executable /usr/bin/blender -svv --rootdir=/tmp/tmpdsh0wnsf --strict-markers --strict-config -c /tmp/tmpdsh0wnsf/pytest.ini
Blender 2.82 (sub 7)
Read prefs: /home/foo/.config/blender/2.82/config/userpref.blend
=================== test session starts ===================
platform linux -- Python 3.8.10, pytest-7.0.1, pluggy-0.13.1 -- /usr/bin/blender
cachedir: .pytest_cache
rootdir: /tmp/tmpyio7hlc2, configfile: pytest.ini
plugins: cov-3.0.0, Faker-12.1.0
collecting ... collected 1 item

tests/test_foo.py::test_foo PASSED

==================== 1 passed in 0.09s ====================
```

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

<a name="blender_addons_dir" href="#blender_addons_dir">#</a>
<b>blender_addons_dir</b> ⇒ `str`

Returns the `scripts/addons` directory of Blender (see
[Blender Directory Layout]), the directory in which by default are located
the addons installed using the
[`install_addons_from_dir`](#install_addons_from_dir) fixture.

It tries to get it using the `BLENDER_USER_SCRIPTS` environment variable, but
if is not defined attempts to discover it from the `PATH`.

<a name="install_addons_from_dir" href="#install_addons_from_dir">#</a>
<b>install_addons_from_dir</b>(<i>addons_dir</i>, <i>addon_ids=None</i>,
<i>save_userpref=True</i>, <i>default_set=True</i>, <i>persistent=True</i>,
<i>quiet=True</i>, <i>\*\*kwargs</i>) ⇒ `list`

Function that installs and enables a set of addons which are located in
a directory. By "addons" Blender understands Python scripts whose file names
end with `.py`, `.zip` files for compressed packages with multiple modules
or directories for Python packages which contain a `__init__.py` file.

This function is designed to be executed before the pytest session
to install the addons that you want to test, using the others fixtures
[`disable_addons`](#disable_addons) or [`uninstall_addons`](#uninstall_addons)
to disable or remove them after the execution of the test suite:

```python
import pytest

@pytest.fixture(scope="session", autouse=True)
def register_addons(install_addons_from_dir, disable_addons):
    addons_ids = install_addons_from_dir("src")
    yield
    disable_addons(addons_ids)
```

```python
import pytest

@pytest.fixture(scope="session", autouse=True)
def register_addons(install_addons_from_dir, uninstall_addons):
    addons_ids = install_addons_from_dir("src")
    yield
    uninstall_addons(addons_ids)
```

The difference between disabling addons and uninstalling them is that disabling
removes the files from the Blender's addons directory but disabling keep the
files there, allowing you to enable it manually from the preferences.

- **addons_dir** (str) Directory in whose root are located the files of the
 addons.
- **addons_ids** (list) Identifiers of the addons modules, packages or ZIP
 files (without extensions) to install. If not defined (default) all Python
 modules, Python packages and ZIP files containing addon packages or modules
 located at the root of the `addons_dir` directory will be installed.
 These identifiers are either:
  - The name of the module for addons composed by a single file
   (`[identifier].py`).
  - The name of the directory for addons composed by a package.
  - The name of the ZIP file without extension for addons composed by a
   ZIP file (`[identifier].zip`).
- **save_userpref** (bool) Save user preferences after installation calling
 [`bpy.ops.wm.save_userpref`]
- **default_set** (bool) Set the user-preference calling `addon_utils.enable`.
- **persistent** (bool) Ensure that the addon is enabled for the entire
 session, after loading new files.
 - **quiet** (bool) If enabled, don't show standard output produced
 installing addons.
- **\*\*kwargs** (dict) Subsecuent keyword arguments are passed to
 [`bpy.ops.preferences.addon_install`].

Returns the addons identifiers as a list, ready to be passed to
[`disable_addons`](#disable_addons) or [`uninstall_addons`](#uninstall_addons).

<a name="disable_addons" href="#disable_addons">#</a>
<b>disable_addons</b>(<i>addons_ids</i>, <i>save_userpref=True</i>,
<i>default_set=True</i>, <i>quiet=True</i>, <i>\*\*kwargs</i>)

Function that disables a set of addons by addons identifiers. Is designed
to disable your addons after a pytest suite execution (check
[`install_addons_from_dir`](#install_addons_from_dir) for an example).

- **addons_ids** (list) Identifiers of the addons modules as are returned by
 [`install_addons_from_dir`](#install_addons_from_dir).
- **save_userpref** (bool) Save user preferences after installation.
- **default_set** (bool) Set the user-preference calling `addon_utils.disable`.
- **quiet** (bool) If enabled, don't show stdout produced disabling addons.
- **\*\*kwargs** (dict) Subsecuent keyword arguments are passed to 
 `addon_utils.disable`.

<a name="uninstall_addons" href="#uninstall_addons">#</a>
<b>uninstall_addons</b>(<i>addons_ids</i>, <i>quiet=True</i>)

Function that uninstall a set of addons by addon identifiers. Is designed to
remove your addons from the Blender's addons directory after a pytest suite
execution (check [`install_addons_from_dir`](#install_addons_from_dir)
for an example).

- **addons_ids** (list) Name of the addons modules as is returned by
 [`install_addons_from_dir`](#install_addons_from_dir).
- **quiet** (bool) If enabled, don't show stdout produced disabling addons.

### Arguments propagation

When you call `pytest`, all options like `--blender-executable` are passed
to the `pytest` suite running `pytest-blender`. If you want to pass arguments
to `blender` in its headless execution, add a `--` between `pytest` and
`blender` arguments.
For example:

```sh
pytest -svv --blender-executable ~/blender -- --debug
```

### CI integration

You can use [blender-downloader] to download multiple
versions of Blender in your CI and test against them. There is an example
for Github Actions in the CI configuration of this repository, something
like:

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
          - '3.1.2'
          - '2.93.9'
          - '2.83.9'
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python v3.9
        uses: actions/setup-python@v3
        with:
          python-version: 3.9
      - name: Upgrade PIP
        run: python -m pip install --upgrade pip
      - name: Cache Blender ${{ matrix.blender-version }}
        uses: actions/cache@v3
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
          printf "%s" "$(blender-downloader \
          ${{ matrix.blender-version }} --extract --remove-compressed \
          --quiet --print-blender-executable)" > _blender-executable-path.txt
      - name: Install dependencies
        id: install-dependencies
        run: |
          python -m pip install .[test]
          blender_executable="$(< _blender-executable-path.txt)"
          python_blender_executable="$(pytest-blender --blender-executable $blender_executable)"
          $python_blender_executable -m ensurepip
          $python_blender_executable -m pip install pytest
          echo "::set-output name=blender-executable::$blender_executable"
      - name: Test with pytest
        run: pytest -svv --blender-executable "${{ steps.install-dependencies.outputs.blender-executable }}" tests
```

### Versions compatibility

- Latest version that officially supports Python3.6 is [v1.2.1].


[pypi-link]: https://pypi.org/project/pytest-blender
[pypi-version-badge-link]: https://img.shields.io/pypi/v/pytest-blender?logo=pypi&logoColor=white
[pypi-pyversions-badge-link]: https://img.shields.io/pypi/pyversions/pytest-blender?logo=python&logoColor=white
[license-image]: https://img.shields.io/pypi/l/pytest-blender?color=light-green&logo=freebsd&logoColor=white
[license-link]: https://github.com/mondeja/pytest-blender/blob/master/LICENSE
[tests-image]: https://img.shields.io/github/workflow/status/mondeja/pytest-blender/CI?logo=github&label=tests
[tests-link]: https://github.com/mondeja/pytest-blender/actions?query=workflow%3ACI
[pypi-downloads-image]: https://img.shields.io/pypi/dm/pytest-blender?logo=blender&logoColor=white
[pypi-downloads-link]: https://pypistats.org/packages/pytest-blender
[blender-downloader]: https://github.com/mondeja/blender-downloader
[v1.2.1]: https://github.com/mondeja/pytest-blender/releases/tag/v1.2.1
[Blender Directory Layout]: https://docs.blender.org/manual/en/latest/advanced/blender_directory_layout.html
[`bpy.ops.preferences.addon_install`]: https://docs.blender.org/api/current/bpy.ops.preferences.html#bpy.ops.preferences.addon_install
[`bpy.ops.wm.save_userpref`]: https://docs.blender.org/api/current/bpy.ops.wm.html#bpy.ops.wm.save_userpref
[pytest-configuration]: https://docs.pytest.org/en/latest/reference/customize.html?highlight=configuration
