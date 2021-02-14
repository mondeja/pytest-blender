# pytest-blender

Pytest plugin for Blender testing. Executes your pytest tests suite with
Blender in headless mode using their builtin Python interpreter.

## Install

```bash
pip install pytest-blender
```

## Usage

Before execute it, you need to install your testing dependencies using the
builtin Blender Python interpreter. To get the interpreter location you can
use the CLI utility `pytest-blender`, so the commands would be something like:

```bash
blender_python="$(pytest-blender)"
$blender_python -m ensurepip
$blender_python -m pip install -r test-requirements.txt
```

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
metadata: {'Python': '3.8.5', 'Platform': 'Linux-5.4.0-65-generic-x86_64-with-glibc2.29', 'Packages': {'pytest': '6.1.2', 'py': '1.9.0', 'pluggy': '0.13.1'}, 'Plugins': {'metadata': '1.11.0', 'cov': '2.10.1', 'html': '3.1.1'}}
rootdir: /home/mondeja/files/code/pytest-blender
plugins: metadata-1.11.0, cov-2.10.1, html-3.1.1
collected 1 item

tests/test_import_bpy.py::test_inside_blender <module 'bpy' from '/usr/share/blender/scripts/modules/bpy/__init__.py'>
PASSED
=========================== 1 passed in 0.01s =================================
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

tests/test_import_bpy.py .                                                [100%]

============================== 1 passed in 0.00s ==============================
```
