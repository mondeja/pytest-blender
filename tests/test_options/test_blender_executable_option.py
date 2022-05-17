from testing_utils import empty_test

from pytest_blender.utils import which_blender


blender_executable = which_blender()
blender_executable_test = f"""
def test_blender_executable(blender_executable):
    assert blender_executable == "{blender_executable}"
"""


def test_blender_executable_cli_option_not_exists(testing_context):
    with testing_context(
        force_empty_inicfg=True,
        files={
            "tests/test_foo.py": empty_test,
        },
    ) as ctx:
        _, stderr, exitcode = ctx.run(
            [
                "--blender-executable",
                "foobarbazimpossibletoexist",
                "--pytest-blender-debug",
            ]
        )
        assert exitcode == 3, stderr
        assert "No such file or directory: 'foobarbazimpossibletoexist'" in stderr


def test_blender_executable_cli_option_exists(testing_context):
    with testing_context(
        force_empty_inicfg=True,
        files={
            "tests/test_blender_executable.py": blender_executable_test,
        },
    ) as ctx:
        _, stderr, exitcode = ctx.run(["--blender-executable", blender_executable])
        assert exitcode == 0, stderr


def test_blender_executable_inicfg_option_not_exists(testing_context):
    with testing_context(
        files={
            "tests/test_foo.py": empty_test,
            "pytest.ini": (
                "[pytest]\nblender-executable = foobarbazimpossibletoexist\n"
            ),
        },
    ) as ctx:
        _, stderr, exitcode = ctx.run()
        assert exitcode == 3, stderr
        assert "No such file or directory: 'foobarbazimpossibletoexist'" in stderr


def test_blender_executable_inicfg_option_exists(testing_context):
    with testing_context(
        files={
            "tests/test_blender_executable.py": blender_executable_test,
            "pytest.ini": (f"[pytest]\nblender-executable = {blender_executable}\n"),
        },
    ) as ctx:
        _, stderr, exitcode = ctx.run()
        assert exitcode == 0, stderr
