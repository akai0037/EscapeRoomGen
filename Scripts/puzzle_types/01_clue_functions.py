close_tool()
print(L.rename_graph.__doc__[:200])
SL = '/Script/Engine.KismetStringLibrary:'; ML = '/Script/Engine.KismetMathLibrary:'
strT = L.get_basic_type_by_name('string'); intT = L.get_basic_type_by_name('int'); boolT = L.get_basic_type_by_name('bool')
colT = L.get_struct_type(unreal.Color.static_struct())
gn = [str(g) for g in L.list_graph_names(bp)]
if 'UsesPoster_0' in gn and 'UsesPoster' not in gn:
    L.rename_graph(G.get_graph_editor_by_name(bp, 'UsesPoster_0').get_graph(), 'UsesPoster')
def fn(name):
    if name in [str(g) for g in L.list_graph_names(bp)]:
        L.remove_function_graph(bp, name)
    e = G.create_and_edit_function_graph(bp, name)
    e.set_is_pure_function(True)
    return e
def entry(e): return PL.get_owning_node(e.find_graph_entry_pin())
def result(e): return [n for n in e.list_all_nodes() if n.get_class().get_name() == 'K2Node_FunctionResult'][0]
def at(n, x, y): L.set_node_pos(n, unreal.IntPoint(int(x), int(y))); return n
def call(e, path, x=0, y=0, **vals):
    n = e.add_call_function_node(path)
    if n is None: raise RuntimeError('no fn ' + path)
    for k, v in vals.items(): setv(n, k, v)
    return at(n, x, y)
SELF = '/Game/EscapeRoom/Blueprints/BP_RoomGenerator.BP_RoomGenerator_C:'
L.compile_blueprint(bp)

# default note text colour (so non-colour puzzles keep the normal look)
w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
ncls = unreal.EditorAssetLibrary.load_blueprint_class('/Game/EscapeRoom/Blueprints/BP_Note')
tmp = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).spawn_actor_from_class(ncls, unreal.Vector(0, 0, -5000))
c = tmp.get_component_by_class(unreal.TextRenderComponent).get_editor_property('text_render_color')
unreal.get_editor_subsystem(unreal.EditorActorSubsystem).destroy_actor(tmp)
DEF = '(B=%d,G=%d,R=%d,A=%d)' % (c.b, c.g, c.r, c.a); print('note colour', DEF)

# ---------------- ClueText(Index, Piece, Order) -> Out
e = fn('ClueText')
for nm, t in [('Index', intT), ('Piece', strT), ('Order', strT)]: e.add_graph_input_parameter(nm, t)
r1 = e.add_graph_output_parameter('Out', strT); r2 = e.add_return_node()
en = entry(e)
# number / key: the piece with "_" for the digits it hides, e.g. Index 1, Piece "13" -> "__13"
ln = call(e, SL + 'Len', 200, 300); link(en, 'Piece', ln, 'S')
m1 = call(e, ML + 'Multiply_IntInt', 400, 250); link(en, 'Index', m1, 'A'); link(ln, 'ReturnValue', m1, 'B')
left = call(e, SL + 'GetSubstring', 600, 250, SourceString='____', StartIndex=0); link(m1, 'ReturnValue', left, 'Length')
a1 = call(e, ML + 'Add_IntInt', 400, 400, B=1); link(en, 'Index', a1, 'A')
m2 = call(e, ML + 'Multiply_IntInt', 600, 400); link(a1, 'ReturnValue', m2, 'A'); link(ln, 'ReturnValue', m2, 'B')
s4 = call(e, ML + 'Subtract_IntInt', 800, 400, A=4); link(m2, 'ReturnValue', s4, 'B')
right = call(e, SL + 'GetSubstring', 1000, 400, SourceString='____', StartIndex=0); link(s4, 'ReturnValue', right, 'Length')
c1 = call(e, SL + 'Concat_StrStr', 1000, 250); link(left, 'ReturnValue', c1, 'A'); link(en, 'Piece', c1, 'B')
c2 = call(e, SL + 'Concat_StrStr', 1200, 300); link(c1, 'ReturnValue', c2, 'A'); link(right, 'ReturnValue', c2, 'B')
# symbol / colour: "symbol = piece", the symbol is the Index-th one in Order ("& % # @")
i2 = call(e, ML + 'Multiply_IntInt', 400, 600, B=2); link(en, 'Index', i2, 'A')
sym = call(e, SL + 'GetSubstring', 600, 600, Length=1); link(en, 'Order', sym, 'SourceString'); link(i2, 'ReturnValue', sym, 'StartIndex')
dec = call(e, SELF + 'Decorate', 800, 600); link(sym, 'ReturnValue', dec, 'S')
c3 = call(e, SL + 'Concat_StrStr', 1000, 600, B=' = '); link(dec, 'Out', c3, 'A')
c4 = call(e, SL + 'Concat_StrStr', 1200, 600); link(c3, 'ReturnValue', c4, 'A'); link(en, 'Piece', c4, 'B')
up = call(e, SELF + 'UsesPoster', 200, 100)
br = at(e.add_branch_node(), 400, 0); link(en, 'then', br, 'execute'); link(up, 'Out', br, 'Condition')
link(br, 'then', r1, 'execute'); link(c4, 'ReturnValue', r1, 'Out'); at(r1, 1500, 0)
link(br, 'else', r2, 'execute'); link(c2, 'ReturnValue', r2, 'Out'); at(r2, 1500, 300)

# ---------------- ClueColor(Index, Order) -> Out (Color): colour puzzle only, else the normal note colour
e = fn('ClueColor')
for nm, t in [('Index', intT), ('Order', strT)]: e.add_graph_input_parameter(nm, t)
r = e.add_graph_output_parameter('Out', colT); en = entry(e); link(en, 'then', r, 'execute')
i2 = call(e, ML + 'Multiply_IntInt', 200, 200, B=2); link(en, 'Index', i2, 'A')
sym = call(e, SL + 'GetSubstring', 400, 200, Length=1); link(en, 'Order', sym, 'SourceString'); link(i2, 'ReturnValue', sym, 'StartIndex')
fs = call(e, SL + 'FindSubstring', 600, 200, SearchIn='&%#@'); link(sym, 'ReturnValue', fs, 'Substring')
p1 = call(e, ML + 'Add_IntInt', 800, 200, B=1); link(fs, 'ReturnValue', p1, 'A')
pt = at(e.add_get_member_variable_node('PuzzleType'), 400, 400)
eq = call(e, ML + 'EqualEqual_IntInt', 600, 400, B=2); link(pt, 'PuzzleType', eq, 'A')
bi = call(e, ML + 'Conv_BoolToInt', 800, 400); link(eq, 'ReturnValue', bi, 'InBool')
mm = call(e, ML + 'Multiply_IntInt', 1000, 300); link(p1, 'ReturnValue', mm, 'A'); link(bi, 'ReturnValue', mm, 'B')
sel = at(e.create_node_from_name('Utilities|Select', unreal.Vector2D(1200, 200), []), 1200, 200)
for _ in range(3): e.add_node_pin(sel)
link(sel, 'ReturnValue', r, 'Out'); link(mm, 'ReturnValue', sel, 'Index'); at(r, 1500, 0)
print([k for k in pins(sel)])
opts = [DEF, '(B=0,G=0,R=210,A=255)', '(B=220,G=60,R=0,A=255)', '(B=0,G=150,R=0,A=255)', '(B=0,G=120,R=235,A=255)']
for i, v in enumerate(opts): setv(sel, 'Option %d' % i, v)

L.compile_blueprint(bp)
for g in ['UsesPoster', 'Decorate', 'ClueText', 'ClueColor', 'GenerateRoom']:
    ed = G.get_graph_editor_by_name(bp, g)
    print(g, 'errors:', [str(L.get_node_title(n)) for n in ed.list_nodes_with_errors()])
print('funcs', [str(f.name) for f in L.list_functions(bp)])
gen = [a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors() if a.get_class().get_name() == 'BP_RoomGenerator_C'][0]
for t in range(3):
    gen.set_editor_property('PuzzleType', t)
    print('type', t, [gen.call_method('ClueText', (i, p, '# @ & %')) for i, p in [(0, '2113'), (0, '21'), (1, '13'), (2, '1')]],
          gen.call_method('Decorate', ('# @ & %',)), [str(gen.call_method('ClueColor', (i, '# @ & %'))) for i in range(2)])
gen.set_editor_property('PuzzleType', 0)
