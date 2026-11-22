"""Runs when the project opens: load this project's copy of er_tool (the Escape Room
Generator panel) so the Escape Room menu always opens the up-to-date version."""
import importlib.util, os, sys
_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "er_tool.py")
_spec = importlib.util.spec_from_file_location("er_tool", _path)
_mod = importlib.util.module_from_spec(_spec)
sys.modules["er_tool"] = _mod
_spec.loader.exec_module(_mod)
try:
    _mod.register_menu()
except Exception as e:
    print("er_tool menu:", e)
