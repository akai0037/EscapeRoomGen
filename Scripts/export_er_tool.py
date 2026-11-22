"""Copy the loaded er_tool module source (and init script) into the project so it can be versioned."""
import sys, inspect, os, unreal
proj = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())
dst = os.path.join(proj, 'Content', 'Python')
os.makedirs(dst, exist_ok=True)
m = sys.modules['er_tool']
src = inspect.getsource(m)
open(os.path.join(dst, 'er_tool.py'), 'w', encoding='utf-8').write(src)
print('EXP er_tool', m.__file__, len(src), '->', dst)
