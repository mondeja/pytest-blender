from testing_utils import blender_executable, empty_test


# escape backslashes for Windows
escaped_blender_executable = blender_executable.replace("\\", "\\\\")

blender_executable_test = f"""
def test_blender_executable(blender_executable):
    assert blender_executable == "{escaped_blender_executable}"
"""


def test_blender_executable_cli_option_not_exists(testing_context):
    with testing_context(
        empty_inicfg=True,
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
        assert (
            # unix
            "No such file or directory: 'foobarbazimpossibletoexist'" in stderr
            or
            # windows
            "The system cannot find the file specified" in stderr
        )


def test_blender_executable_cli_option_exists(testing_context):
    with testing_context(
        empty_inicfg=True,
        files={
            "tests/test_blender_executable.py": blender_executable_test,
        },
    ) as ctx:
        stdout, stderr, exitcode = ctx.run(["--blender-executable", blender_executable])
        assert exitcode == 0, f"{stdout}\n---\n{stderr}"


def test_blender_executable_inicfg_option_not_exists(testing_context):
    with testing_context(
        {
            "tests/test_foo.py": empty_test,
            "pytest.ini": (
                "[pytest]\nblender-executable = foobarbazimpossibletoexist\n"
            ),
        },
    ) as ctx:
        _, stderr, exitcode = ctx.run()
        assert exitcode == 3, stderr
        assert (
            # unix
            "No such file or directory: 'foobarbazimpossibletoexist'" in stderr
            or
            # windows
            "The system cannot find the file specified" in stderr
        )


def test_blender_executable_inicfg_option_exists(testing_context):
    with testing_context(
        files={
            "tests/test_blender_executable.py": blender_executable_test,
            "pytest.ini": (f"[pytest]\nblender-executable = {blender_executable}\n"),
        },
    ) as ctx:
        stdout, stderr, exitcode = ctx.run()
        assert exitcode == 0, f"{stdout}\n---\n{stderr}"
