close_tool()
ML = '/Script/Engine.KismetMathLibrary:'; SL = '/Script/Engine.KismetStringLibrary:'
SELF = '/Game/EscapeRoom/Blueprints/BP_RoomGenerator.BP_RoomGenerator_C:'
ed = G.get_graph_editor_by_name(bp, 'GenerateRoom')
N = lambda nm: node(ed, nm)
def pos(n): p = L.get_node_pos(n); return p.x, p.y
def at(n, x, y): L.set_node_pos(n, unreal.IntPoint(int(x), int(y))); return n
def near(n, ref, dx, dy): x, y = pos(ref); return at(n, x + dx, y + dy)
def call(path, ref, dx, dy):
    n = ed.add_call_function_node(path)
    if n is None: raise RuntimeError('no fn ' + path)
    return near(n, ref, dx, dy)
def targets(n, pn): return list(PL.list_connected_pins(pin(n, pn)))
def insert_after(n, outpin, new, newin='execute', newout='then'):
    t = targets(n, outpin); PL.break_pin_links(pin(n, outpin))
    link(n, outpin, new, newin)
    for p in t:
        if not PL.try_create_connection(pin(new, newout), p): raise RuntimeError('relink failed')
order = N('K2Node_SymOrder')
# 1. SymOrder reads the PermIndex variable (so Medium can use it too)
src = [PL.get_owning_node(p).get_name() for p in targets(N('K2Node_SymMul'), 'A')]
print('SymMul.A from', src)
if 'K2Node_VariableSet_4' in src:
    gp = near(ed.add_get_member_variable_node('PermIndex'), N('K2Node_SymMul'), -200, 80)
    link(gp, 'PermIndex', N('K2Node_SymMul'), 'A')
stray = [n for n in ed.list_all_nodes() if n.get_class().get_name() == 'K2Node_VariableSet' and not targets(n, 'execute')]
print('stray', [n.get_name() for n in stray]); ed.remove_nodes(stray)
# 2. Medium rolls a symbol order too
spawnA = N('K2Node_SpawnNoteA')
mset = near(ed.add_set_member_variable_node('PermIndex'), spawnA, -300, -250)
mstr = near(ed.add_get_local_variable_node('Stream'), spawnA, -700, -150)
mrnd = call(ML + 'RandomIntegerInRangeFromStream', spawnA, -500, -150)
link(mstr, 'Stream', mrnd, 'Stream'); setv(mrnd, 'Min', 0); setv(mrnd, 'Max', 23)
link(mrnd, 'ReturnValue', mset, 'PermIndex')
insert_after(N('K2Node_IfThenElse_0'), 'else', mset)
# 3. Medium note texts come from ClueText
for i, half, txt in [(0, 'K2Node_FirstHalf', 'K2Node_Text1'), (1, 'K2Node_SecondHalf', 'K2Node_Text2')]:
    ct = call(SELF + 'ClueText', N(txt), -250, 120)
    setv(ct, 'Index', i); link(N(half), 'ReturnValue', ct, 'Piece'); link(order, 'ReturnValue', ct, 'Order')
    link(ct, 'Out', N(txt), 'InString')
ed.remove_nodes([N('K2Node_Text1Str'), N('K2Node_Text2Str')])
# 4. colour the notes (colour puzzle) right after their text is set
def colour_after(settext, textget, idx):
    st = N(settext)
    c = call('/Script/Engine.TextRenderComponent:SetTextRenderColor', st, 0, 220)
    cc = call(SELF + 'ClueColor', st, -260, 360)
    setv(cc, 'Index', idx); link(order, 'ReturnValue', cc, 'Order'); link(cc, 'Out', c, 'Value')
    link(N(textget), 'Text', c, 'self')
    if targets(st, 'then'): insert_after(st, 'then', c)
    else: link(st, 'then', c, 'execute')
    return c
colour_after('K2Node_SetNoteTextA', 'K2Node_NoteTextCompA', 0)
cB = colour_after('K2Node_SetNoteTextB', 'K2Node_NoteTextCompB', 1)
# 5. Medium -> poster if symbol / colour puzzle
posterStart = N('K2Node_SymPosterSpots')
brM = near(ed.add_branch_node(), cB, 300, 0)
upM = call(SELF + 'UsesPoster', cB, 150, 150); link(upM, 'Out', brM, 'Condition')
link(cB, 'then', brM, 'execute'); link(brM, 'then', posterStart, 'execute')
# 6+7. Hard note texts + colours
for i in range(4):
    ht = N('K2Node_HardText%d' % i)
    ct = call(SELF + 'ClueText', ht, -250, 150)
    setv(ct, 'Index', i); link(N('K2Node_HardDigit%d' % i), 'ReturnValue', ct, 'Piece'); link(order, 'ReturnValue', ct, 'Order')
    link(ct, 'Out', ht, 'InString')
    colour_after('K2Node_HardSetText%d' % i, 'K2Node_HardNoteText%d' % i, i)
ed.remove_nodes([N(n) for n in ['K2Node_HardPre%d' % i for i in range(4)] + ['K2Node_HardSuf%d' % i for i in range(4)] + ['K2Node_Sym%d' % i for i in range(4)]])
# 8. Hard: poster only for symbol / colour
rem3 = N('K2Node_HardRemove3')
brH = near(ed.add_branch_node(), rem3, 300, 250)
upH = call(SELF + 'UsesPoster', rem3, 150, 400); link(upH, 'Out', brH, 'Condition')
insert_after(rem3, 'then', brH)
# 9. Poster text: first 2 or 4 symbols (Medium / Hard), as colour words on the colour puzzle
ot = N('K2Node_SymOrderText')
gd = near(ed.add_get_member_variable_node('Difficulty'), ot, -900, 150)
mul = call(ML + 'Multiply_IntInt', ot, -700, 150); link(gd, 'Difficulty', mul, 'A'); setv(mul, 'B', 4)
sub = call(ML + 'Subtract_IntInt', ot, -520, 150); link(mul, 'ReturnValue', sub, 'A'); setv(sub, 'B', 1)
ss = call(SL + 'GetSubstring', ot, -340, 150); link(order, 'ReturnValue', ss, 'SourceString'); setv(ss, 'StartIndex', 0); link(sub, 'ReturnValue', ss, 'Length')
dec = call(SELF + 'Decorate', ot, -160, 150); link(ss, 'ReturnValue', dec, 'S'); link(dec, 'Out', ot, 'InString')
L.compile_blueprint(bp)
print('errors', [str(L.get_node_title(n)) for n in ed.list_nodes_with_errors()], 'warn', [str(L.get_node_title(n)) for n in ed.list_nodes_with_warnings()])
# ---- test in the editor world
AS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
gen = [a for a in AS.get_all_level_actors() if a.get_class().get_name() == 'BP_RoomGenerator_C'][0]
def notes(): return [a for a in AS.get_all_level_actors() if a.get_class().get_name() == 'BP_Note_C']
def txt(n):
    c = n.get_component_by_class(unreal.TextRenderComponent); col = c.get_editor_property('text_render_color')
    par = n.get_attach_parent_actor()
    return '%s%s@%s' % (c.get_editor_property('text'), '' if col.r == 20 and col.g == 20 else '(%d,%d,%d)' % (col.r, col.g, col.b), par.get_actor_label() if par else None)
for d in range(3):
    for t in range(4):
        gen.set_editor_property('Difficulty', d); gen.set_editor_property('PuzzleType', t)
        gen.call_method('GenerateRoom', (7,))
        print('D%d T%d code %04d' % (d, t, gen.get_editor_property('CurrentCode')), [txt(n) for n in notes()])
gen.set_editor_property('PuzzleType', 0); gen.set_editor_property('Difficulty', 0)
