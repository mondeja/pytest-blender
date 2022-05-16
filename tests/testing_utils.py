import pytest


parametrize_plugin_on_off = pytest.mark.parametrize(
    ("plugin_args", "expected_exitcode"),
    (
        pytest.param([], 0, id="plugin_args=[]-exitcode=0"),
        pytest.param(
            ["-p", "no:pytest-blender"],
            1,
            id='plugin_args=["-p", "no:pytest-blender"]-exitcode=1',
        ),
    ),
)
