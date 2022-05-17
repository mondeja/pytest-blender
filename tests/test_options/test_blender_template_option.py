import os

import pytest
from testing_utils import empty_test

from pytest_blender import get_blender_version, which_blender
from pytest_blender.utils import parse_version


blender_userpref_expected_location = os.path.join(
    os.path.expanduser("~"),
    ".config",
    "blender",
    ".".join(
        [str(num) for num in parse_version(get_blender_version(which_blender()))[:2]]
    ),
    "config",
    "userpref.blend",
)

skip_if_userpref_does_not_exists = pytest.mark.skipif(
    not os.path.isfile(blender_userpref_expected_location),
    reason=(
        f"The file '{blender_userpref_expected_location}' must exist"
        " in order to run this test."
    ),
)


def assert_userpref_file_read(stdout, stderr):
    assert f"Read blend: {blender_userpref_expected_location}" in stdout
    assert "Error:" not in stdout
    assert "Error:" not in stderr
    assert "No such file or directory" not in stdout
    assert "No such file or directory" not in stderr


@skip_if_userpref_does_not_exists
def test_blender_template_cli_option(testing_context):
    with testing_context(
        force_empty_inicfg=True,
        files={"tests/test_foo.py": empty_test},
    ) as ctx:
        stdout, stderr, _ = ctx.run(
            [
                "--blender-template",
                blender_userpref_expected_location,
            ]
        )
        assert_userpref_file_read(stdout, stderr)


@skip_if_userpref_does_not_exists
def test_blender_template_inicfg_option(testing_context):
    with testing_context(
        files={
            "tests/test_foo.py": empty_test,
            "pytest.ini": f"""[pytest]
blender-template = {blender_userpref_expected_location}
""",
        },
    ) as ctx:
        stdout, stderr, _ = ctx.run()
        assert_userpref_file_read(stdout, stderr)
