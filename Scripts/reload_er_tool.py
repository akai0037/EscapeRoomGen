"""Swap the open Escape Room Generator panel for the project's updated er_tool.py (no restart)."""
import sys, unreal
old = sys.modules.get('er_tool')
try:
    if old and getattr(old, '_window', None):
        old._window.close()
except Exception as e:
    print('RELOAD close', e)
proj = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())
exec(open(proj + 'Content/Python/init_unreal.py', encoding='utf-8').read(), {'__file__': proj + 'Content/Python/init_unreal.py', '__name__': 'er_init'})
import er_tool
if old and getattr(old, '_tick', None):
    er_tool._tick = old._tick          # reuse the existing Qt pump
    er_tool._app = old._app
w = er_tool.show()
print('RELOAD ok', er_tool.__file__, w.difficulty.count())
