import sys


pytest_blender_unactive = "-p" in sys.argv and "no:pytest-blender" in sys.argv
pytest_blender_active = not pytest_blender_unactive
