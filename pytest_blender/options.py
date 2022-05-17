OPTIONS = {
    "blender-executable": {"help": "Blender executable location."},
    "blender-template": {
        "help": "Open Blender using a custom layout as start template."
    },
    "blender-addons-dirs": {
        "help": "Directory with addons to install before test suite execution.",
        "opts": {"nargs": "+", "default": []},
    },
    "blender-addons-cleaning": {
        "help": (
            "What to do with addons installed after test suite execution."
            " It accepts one of the next strings: 'uninstall' (default,"
            " remove addons from Blender's user repository after testing),"
            " 'disable' (just disable the addons in Blender preferences)"
            " or 'keep' (keep the addons installed after testing, useful"
            " for manual reviews)."
        ),
        "opts": {"default": "uninstall", "choices": ["uninstall", "disable", "keep"]},
    },
    "pytest-blender-debug": {
        "help": (
            "Enable internal plugin debugging capabilities to show some useful"
            " information to STDOUT like the command used to start Blender"
            " executing the test suite."
        ),
        "opts": {"action": "store_true"},
    },
}
