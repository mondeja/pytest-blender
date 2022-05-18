import os


library_and_test_files = {
    "tests/test_my_foo_library.py": """
import os
import sys

if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())

from my_foo_library.functions import my_foo_function

def test_my_foo_library():
    assert my_foo_function()
""",
    "my_foo_library/__init__.py": "",
    "my_foo_library/functions.py": """
def my_foo_function():
    return True
""",
}


def test_coverage_with_pytest_cov(testing_context):
    with testing_context(empty_inicfg=True, files=library_and_test_files) as ctx:
        stdout, stderr, exitcode = ctx.run(["--cov=my_foo_library"])
        _inside_coverage, functions_mod_cov_line = (False, None)
        for line in stdout.splitlines():
            if not _inside_coverage:
                if "coverage:" in line:
                    _inside_coverage = True
            elif line.startswith("my_foo_library/functions.py"):
                functions_mod_cov_line = line

        assert " 2 " in functions_mod_cov_line  # statements
        assert " 0 " in functions_mod_cov_line  # missed
        assert "100%" in functions_mod_cov_line  # covered

        coverage_data_file = os.path.join(ctx.rootdir, ".coverage")
        assert os.path.isfile(coverage_data_file)

        assert exitcode == 0, stderr
