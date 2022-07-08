import os


library_and_test_files = {
    "tests/__init__.py": "",
    "tests/test_my_foo_library.py": """
import os
import sys

from src.my_foo_library.functions import my_foo_function

def test_my_foo_library():
    assert my_foo_function()
""",
    "src/my_foo_library/__init__.py": "bl_info = {'name': 'My Foo Library'}",
    "src/my_foo_library/functions.py": """
def my_foo_function():
    return True
""",
}


def test_coverage_with_pytest_cov(testing_context):
    with testing_context(empty_inicfg=True, files=library_and_test_files) as ctx:
        stdout, stderr, exitcode = ctx.run(["--cov=src/my_foo_library"])
        msg = f"{stdout}\n----\n{stderr}"

        assert stdout.count("100%") == 3, msg
        coverage_data_file = os.path.join(ctx.rootdir, ".coverage")
        assert os.path.isfile(coverage_data_file), msg

        assert exitcode == 0, msg


def test_coverage_with_pytest_cov_blender_addons_dir(testing_context):
    with testing_context(empty_inicfg=True, files=library_and_test_files) as ctx:
        if os.path.isfile(os.path.join(ctx.rootdir, ".coverage")):
            os.remove(os.path.join(ctx.rootdir, ".coverage"))
        with open(os.path.join(ctx.rootdir, "pytest.ini"), "a") as f:
            f.write(
                """pytest-blender-debug = true
blender-addons-dirs = src
addopts = --cov src/my_foo_library
"""
            )
        stdout, stderr, exitcode = ctx.run([])
        msg = f"{stdout}\n----\n{stderr}"

        assert stdout.count("100%") == 3, msg
        coverage_data_file = os.path.join(ctx.rootdir, ".coverage")
        assert os.path.isfile(coverage_data_file), msg

        assert exitcode == 0, msg


def test_coverage_with_pytest_cov_pythonpath(testing_context):
    with testing_context(files=library_and_test_files) as ctx:
        if os.path.isfile(os.path.join(ctx.rootdir, ".coverage")):
            os.remove(os.path.join(ctx.rootdir, ".coverage"))
        stdout, stderr, exitcode = ctx.run(
            ["--cov=src/my_foo_library", "--pytest-blender-debug"],
            ["--python-use-system-env"],
            env={"PYTHONPATH": "src"},
        )

        msg = f"{stdout}\n----\n{stderr}"

        assert stdout.count("100%") == 3, msg
        coverage_data_file = os.path.join(ctx.rootdir, ".coverage")
        assert os.path.isfile(coverage_data_file), msg

        assert exitcode == 0, msg
