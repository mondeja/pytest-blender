import os


def test_blender_cli_arguments_propagation(testing_context):
    """CLI arguments propagation."""
    with testing_context(
        {
            "tests/test_blender_argv.py": """
import sys

def test_blender_argv():
    assert '--debug' in sys.argv
"""
        }
    ) as ctx:
        stdout, stderr, exitcode = ctx.run(["--", "--debug"])
        assert exitcode == 0, stderr

        # Blender debugging information with `--debug`
        assert "argv[2] = --debug" in stdout, stderr


def test_cli_env_propagation(testing_context):
    """Environment variables propagation."""
    custom_pyc_files_dirname = "custom_pyc_files_dir"
    with testing_context(
        {
            "tests/test_python_cache_prefix.py": f"""
import os

def test_python_cache_prefix():
    python_cache_prefix = os.environ.get("PYTHONPYCACHEPREFIX")
    assert os.path.basename(python_cache_prefix) == "{custom_pyc_files_dirname}"
    print(python_cache_prefix)
""",
            os.path.join(custom_pyc_files_dirname, "empty.txt"): "",
        }
    ) as ctx:
        custom_pyc_files_dir = os.path.join(ctx.rootdir, custom_pyc_files_dirname)
        stdout, stderr, exitcode = ctx.run(
            [],
            env={"PYTHONPYCACHEPREFIX": custom_pyc_files_dir},
        )
        assert exitcode == 0, stderr
        assert custom_pyc_files_dir in stdout

        # pyc files directories added
        assert len(custom_pyc_files_dir) > 1


def test_enable_plugin_explicitly_from_pytest_cli(testing_context):
    with testing_context(
        {
            "tests/test_no_explicit_enabling.py": """
import sys

def test_no_explicit_pytest_blender_plugin_enabling():
    assert '-p' not in sys.argv
    assert 'pytest-blender' not in sys.argv
""",
        }
    ) as ctx:
        # if we explicitly enable pytest-blender using `-p pytest-blender`
        # the tests itself are tried to be executed with pytest-blender
        # which could result in a infinite loop, but is not the case because
        # the arguments are malformed in the second execution
        #
        # the solution here is to remove the invalid argument in the Blender
        # execution at `plugin.py`
        stdout, stderr, exitcode = ctx.run(
            ["-p", "pytest-blender", "--pytest-blender-debug"]
        )
        assert exitcode == 0, stderr
        assert "-p pytest-blender" not in stdout
