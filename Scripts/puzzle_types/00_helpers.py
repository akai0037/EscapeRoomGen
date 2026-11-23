# bridge: no-transaction
import unreal
G = unreal.BlueprintGraphEditor; L = unreal.BlueprintEditorLibrary; PL = unreal.BlueprintGraphPinLibrary
BP_PATH = '/Game/EscapeRoom/Blueprints/BP_RoomGenerator'
bp = unreal.load_asset(BP_PATH)
def pins(n): return {str(PL.get_pin_name(p)): p for p in L.list_all_pins(n)}
def pin(n, name):
    d = pins(n)
    if name not in d: raise RuntimeError('no pin %s on %s; has %s' % (name, n.get_name(), list(d)))
    return d[name]
def link(a, an, b, bn):
    pa, pb = pin(a, an), pin(b, bn)
    if not PL.try_create_connection(pa, pb):
        raise RuntimeError('link failed %s.%s -> %s.%s' % (a.get_name(), an, b.get_name(), bn))
def setv(n, name, v): PL.set_pin_value(pin(n, name), str(v))
def node(ed, name):
    for n in ed.list_all_nodes():
        if n.get_name() == name: return n
    raise RuntimeError('no node ' + name)
def show(n):
    print('  NODE', n.get_name(), str(L.get_node_title(n)).replace('\n', ' '), [(k, PL.get_pin_type_display_string(p)) for k, p in pins(n).items()])
def close_tool():
    import sys
    m = sys.modules.get('er_tool')
    if m is None: return
    try:
        if m._window is not None: m._window.close(); m._window.deleteLater()
    except Exception as e: print('close win', e)
    m._window = None
    try:
        if m._tick is not None: unreal.unregister_slate_post_tick_callback(m._tick)
    except Exception as e: print('untick', e)
    m._tick = None
    print('tool panel closed')
