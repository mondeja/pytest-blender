from pytest_blender.plugin import get_options_cli_args_and_skip_count


def test_skip_count_of_defined_options():
    skip_count = get_options_cli_args_and_skip_count()
    assert 2 == skip_count["--blender-executable"]
    assert 2 == skip_count["--blender-addons-dirs"]
    assert 2 == skip_count["--blender-addons-cleaning"]
    assert 1 == skip_count["--pytest-blender-debug"]


def test_skip_count_of_custom_options():
    custom_options = {
        "bool-true": {"help": "true flag option", "opts": {"action": "store_true"}},
        "bool-false": {
            "help": "false flag option",
            "opts": {"action": "store_false"},
        },
        "value": {"help": "value option"},
        "value-with-default": {
            "help": "value option with default",
            "opts": {"default": "test"},
        },
    }
    skip_count = get_options_cli_args_and_skip_count(custom_options)
    assert 1 == skip_count["--bool-true"]
    assert 1 == skip_count["--bool-false"]
    assert 2 == skip_count["--value"]
    assert 2 == skip_count["--value-with-default"]
