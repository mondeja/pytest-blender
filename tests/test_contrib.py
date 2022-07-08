import os


test_files = {"tests/__init__.py": ""}

create_lib_tests_py = (
    lambda package_dotpath: f"""
import os
import sys

from {package_dotpath}.functions import my_foo_function

def test_my_foo_library():
    assert my_foo_function()
"""
)
create_init_py = lambda: "bl_info = {'name': 'My Foo Library'}"
create_functions_py = (
    lambda: """
def my_foo_function():
    return True
"""
)


def test_coverage_with_pytest_cov(testing_context):
    files = test_files
    files.update(
        {
            "tests/test_one_two_library.py": create_lib_tests_py("one.two"),
            "one/two/__init__.py": create_init_py(),
            "one/two/functions.py": create_functions_py(),
        }
    )
    with testing_context(empty_inicfg=True, files=files) as ctx:
        stdout, stderr, exitcode = ctx.run(["--cov=one/two"])
        msg = f"{stdout}\n----\n{stderr}"

        assert stdout.count("100%") == 3, msg
        coverage_data_file = os.path.join(ctx.rootdir, ".coverage")
        assert os.path.isfile(coverage_data_file), msg

        assert exitcode == 0, msg


def test_coverage_with_pytest_cov_pythonpath(testing_context):
    files = test_files
    files.update(
        {
            "tests/test_three_four_library.py": create_lib_tests_py("three.four"),
            "three/four/__init__.py": create_init_py(),
            "three/four/functions.py": create_functions_py(),
        }
    )
    with testing_context(files=files) as ctx:
        if os.path.isfile(os.path.join(ctx.rootdir, ".coverage")):
            os.remove(os.path.join(ctx.rootdir, ".coverage"))
        stdout, stderr, exitcode = ctx.run(
            [
                "--cov=three/four",
                "--pytest-blender-debug",
                "--import-mode=importlib",
            ],
            ["--python-use-system-env"],
            env={"PYTHONPATH": os.path.join(ctx.rootdir, "three")},
        )

        msg = f"{stdout}\n----\n{stderr}"

        assert stdout.count("100%") == 3, msg
        coverage_data_file = os.path.join(ctx.rootdir, ".coverage")
        assert os.path.isfile(coverage_data_file), msg

        assert exitcode == 0, msg


def test_coverage_with_pytest_cov_blender_addons_dir(testing_context):
    files = test_files
    files.update(
        {
            "tests/test_five_six_library.py": create_lib_tests_py("five.six"),
            "five/six/__init__.py": create_init_py(),
            "five/six/functions.py": create_functions_py(),
        }
    )
    with testing_context(empty_inicfg=True, files=files) as ctx:
        if os.path.isfile(os.path.join(ctx.rootdir, ".coverage")):
            os.remove(os.path.join(ctx.rootdir, ".coverage"))
        with open(os.path.join(ctx.rootdir, "pytest.ini"), "a") as f:
            f.write(
                """pytest-blender-debug = true
blender-addons-dirs = five
addopts = --cov five/six
"""
            )
        stdout, stderr, exitcode = ctx.run()
        msg = f"{stdout}\n----\n{stderr}"

        assert stdout.count("100%") == 3, msg
        coverage_data_file = os.path.join(ctx.rootdir, ".coverage")
        assert os.path.isfile(coverage_data_file), msg

        assert exitcode == 0, msg


"""
def test_coverage_with_pytest_cov_blender_user_scripts_envvar(testing_context):
    files = test_files
    files.update(
        {
            "tests/test_seven_height_library.py": create_lib_tests_py("seven.height"),
            "seven/height/__init__.py": create_init_py(),
            "seven/height/functions.py": create_functions_py(),
        }
    )
    with testing_context(files=files) as ctx:
        if os.path.isfile(os.path.join(ctx.rootdir, ".coverage")):
            os.remove(os.path.join(ctx.rootdir, ".coverage"))
        stdout, stderr, exitcode = ctx.run(
            ["--cov=seven/height"],
            env={"BLENDER_USER_SCRIPTS": os.path.join(ctx.rootdir, "seven")},
        )

        msg = f"{stdout}\n----\n{stderr}"

        assert stdout.count("100%") == 3, msg
        coverage_data_file = os.path.join(ctx.rootdir, ".coverage")
        assert os.path.isfile(coverage_data_file), msg

        assert exitcode == 0, msg
"""
