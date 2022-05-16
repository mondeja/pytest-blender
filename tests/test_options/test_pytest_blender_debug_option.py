import pytest


def assert_debug_output(output):
    debug_line_found = False
    for line in output.splitlines():
        if line.startswith("[DEBUG (pytest-blender)] Running blender with:"):
            debug_line_found = True
            assert "--strict-markers --strict-config" in line
    assert debug_line_found


def test_pytest_blender_debug_cli_option(testing_context):
    with testing_context(
        files={
            "tests/test_foo.py": "def test_foo():\n    pass",
        },
    ) as ctx:
        stdout, stderr, exitcode = ctx.run(["--pytest-blender-debug"])
        assert_debug_output(stdout)
        assert exitcode == 0, stderr


@pytest.mark.parametrize("option_value", ("true", "foobarbaz", ""))
def test_pytest_blender_debug_inicfg_option(testing_context, option_value):
    with testing_context(
        files={
            "tests/test_foo.py": "def test_foo():\n    pass",
            "pytest.ini": f"[pytest]\npytest-blender-debug = {option_value}",
        },
    ) as ctx:
        stdout, stderr, exitcode = ctx.run()
        assert_debug_output(stdout)
        assert exitcode == 0, stderr
