close_tool()
ML = '/Script/Engine.KismetMathLibrary:'; A = '/Script/Engine.Actor:'; GS = '/Script/Engine.GameplayStatics:'
SELF = '/Game/EscapeRoom/Blueprints/BP_RoomGenerator.BP_RoomGenerator_C:'
intT = L.get_basic_type_by_name('int')
gn = [str(g) for g in L.list_graph_names(bp)]
if 'ApplyKeyPuzzle' in gn: raise RuntimeError('already there')
e = G.create_and_edit_function_graph(bp, 'ApplyKeyPuzzle')
e.add_graph_input_parameter('InSeed', intT)
en = PL.get_owning_node(e.find_graph_entry_pin())
X = [0]
def at(n, x, y): L.set_node_pos(n, unreal.IntPoint(int(x), int(y))); return n
def call(path, x, y):
    n = e.add_call_function_node(path)
    if n is None: raise RuntimeError('no fn ' + path)
    return at(n, x, y)
def defaults(n, **kv):
    for k, v in kv.items(): setv(n, k, v)
# 1. remove keys from the last room
gk = call(GS + 'GetAllActorsOfClass', 250, 0); defaults(gk, ActorClass='/Game/EscapeRoom/Blueprints/BP_Key.BP_Key_C')
fe = at(e.add_macro_node('/Engine/EditorBlueprintResources/StandardMacros.StandardMacros:ForEachLoop'), 550, 0)
dk = call(A + 'K2_DestroyActor', 850, -150)
link(en, 'then', gk, 'execute'); link(gk, 'then', fe, 'Exec'); link(gk, 'OutActors', fe, 'Array')
link(fe, 'LoopBody', dk, 'execute'); link(fe, 'Array Element', dk, 'self')
# 2. the lock box only shows up in the key puzzle; it always starts locked
gb = call(GS + 'GetActorOfClass', 850, 100); defaults(gb, ActorClass='/Game/EscapeRoom/Blueprints/BP_LockBox.BP_LockBox_C')
pt = at(e.add_get_member_variable_node('PuzzleType'), 850, 350)
eq = call(ML + 'EqualEqual_IntInt', 1050, 350); link(pt, 'PuzzleType', eq, 'A'); defaults(eq, B=3)
nt = call(ML + 'Not_PreBool', 1250, 350); link(eq, 'ReturnValue', nt, 'A')
hid = call(A + 'SetActorHiddenInGame', 1150, 100); link(gb, 'ReturnValue', hid, 'self'); link(nt, 'ReturnValue', hid, 'bNewHidden')
col = call(A + 'SetActorEnableCollision', 1450, 100); link(gb, 'ReturnValue', col, 'self'); link(eq, 'ReturnValue', col, 'bNewActorEnableCollision')
rb = call('/Game/EscapeRoom/Blueprints/BP_LockBox.BP_LockBox_C:ResetBox', 1750, 100); link(gb, 'ReturnValue', rb, 'self')
br = at(e.add_branch_node(), 2000, 100); link(eq, 'ReturnValue', br, 'Condition')
link(fe, 'Completed', gb, 'execute'); link(gb, 'then', hid, 'execute'); link(hid, 'then', col, 'execute'); link(col, 'then', rb, 'execute'); link(rb, 'then', br, 'execute')
# 3. key puzzle: pick one note (by seed), move it into the box, put the key where the note was
gn_ = call(GS + 'GetAllActorsOfClass', 2250, 100); defaults(gn_, ActorClass='/Game/EscapeRoom/Blueprints/BP_Note.BP_Note_C')
link(br, 'then', gn_, 'execute')
ln = call('/Script/Engine.KismetArrayLibrary:Array_Length', 2250, 350); link(gn_, 'OutActors', ln, 'TargetArray')
sb = call(ML + 'Subtract_IntInt', 2450, 350); link(ln, 'ReturnValue', sb, 'A'); defaults(sb, B=1)
ad = call(ML + 'Add_IntInt', 2250, 500); link(en, 'InSeed', ad, 'A'); defaults(ad, B=99)
ms = call(ML + 'MakeRandomStream', 2450, 500); link(ad, 'ReturnValue', ms, 'InitialSeed')
rn = call(ML + 'RandomIntegerInRangeFromStream', 2650, 400); link(ms, 'ReturnValue', rn, 'Stream'); defaults(rn, Min=0); link(sb, 'ReturnValue', rn, 'Max')
ag = call('/Script/Engine.KismetArrayLibrary:Array_Get', 2850, 300)
print('Array_Get', ag.get_class().get_name(), list(pins(ag)))
link(gn_, 'OutActors', ag, list(pins(ag))[0]); link(rn, 'ReturnValue', ag, list(pins(ag))[1])
noteP = list(pins(ag))[2]
sp = call(A + 'GetAttachParentActor', 3050, 450); link(ag, noteP, sp, 'self')
sx = call(A + 'GetTransform', 3250, 450); link(sp, 'ReturnValue', sx, 'self')
gt = call(GS + 'GetAllActorsWithTag', 2550, 100); defaults(gt, Tag='BoxSpot'); link(gn_, 'then', gt, 'execute')
bg = call('/Script/Engine.KismetArrayLibrary:Array_Get', 2850, 150); link(gt, 'OutActors', bg, list(pins(bg))[0]); defaults(bg, **{list(pins(bg))[1]: 0})
bx = call(A + 'GetTransform', 3050, 150); link(bg, list(pins(bg))[2], bx, 'self')
st = call(A + 'K2_SetActorTransform', 3300, 0); link(ag, noteP, st, 'self'); link(bx, 'ReturnValue', st, 'NewTransform')
at1 = call(A + 'K2_AttachToActor', 3600, 0); link(ag, noteP, at1, 'self'); link(bg, list(pins(bg))[2], at1, 'ParentActor')
for r in ['LocationRule', 'RotationRule', 'ScaleRule']: defaults(at1, **{r: 'KeepWorld'})
sk = call(GS + 'BeginDeferredActorSpawnFromClass', 3900, 0); defaults(sk, ActorClass='/Game/EscapeRoom/Blueprints/BP_Key.BP_Key_C'); link(sx, 'ReturnValue', sk, 'SpawnTransform')
print('spawn pins', list(pins(sk)))
fs = call(GS + 'FinishSpawningActor', 4200, 0); link(sk, 'ReturnValue', fs, 'Actor'); link(sx, 'ReturnValue', fs, 'SpawnTransform')
at2 = call(A + 'K2_AttachToActor', 4500, 0); link(fs, 'ReturnValue', at2, 'self'); link(sp, 'ReturnValue', at2, 'ParentActor')
for r in ['LocationRule', 'RotationRule', 'ScaleRule']: defaults(at2, **{r: 'KeepWorld'})
link(gt, 'then', st, 'execute'); link(st, 'then', at1, 'execute'); link(at1, 'then', sk, 'execute'); link(sk, 'then', fs, 'execute'); link(fs, 'then', at2, 'execute')
L.compile_blueprint(bp)
print('fn errors', [str(L.get_node_title(n)) for n in e.list_nodes_with_errors()])
# ---- call it at the end of every branch of GenerateRoom
ed = G.get_graph_editor_by_name(bp, 'GenerateRoom')
N = lambda nm: node(ed, nm)
entryG = [n for n in ed.list_all_nodes() if n.get_class().get_name() == 'K2Node_FunctionEntry'][0]
brs = [n for n in ed.list_all_nodes() if n.get_class().get_name() == 'K2Node_IfThenElse' and any('UsesPoster' in PL.get_owning_node(q).get_name() or 'UsesPoster' in str(L.get_node_title(PL.get_owning_node(q))) for q in PL.list_connected_pins(pin(n, 'Condition')))]
print('poster branches', [b.get_name() for b in brs])
ends = [(N('K2Node_CallFunction_8'), 'then'), (N('K2Node_SymPaperScale'), 'then')] + [(b, 'else') for b in brs]
for n, p in ends:
    if list(PL.list_connected_pins(pin(n, p))): print('WARN already linked', n.get_name(), p); continue
    c = ed.add_call_function_node(SELF + 'ApplyKeyPuzzle'); pp = L.get_node_pos(n); L.set_node_pos(c, unreal.IntPoint(pp.x + 300, pp.y + 120))
    link(n, p, c, 'execute'); link(entryG, 'InSeed', c, 'InSeed')
L.compile_blueprint(bp)
print('gen errors', [str(L.get_node_title(n)) for n in ed.list_nodes_with_errors()])
AS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
gen = [a for a in AS.get_all_level_actors() if a.get_class().get_name() == 'BP_RoomGenerator_C'][0]
def txt(n):
    c = n.get_component_by_class(unreal.TextRenderComponent); par = n.get_attach_parent_actor()
    return '%s@%s' % (c.get_editor_property('text'), par.get_actor_label() if par else None)
for d in range(3):
    for t in (3, 1):
        for seed in (7, 8):
            gen.set_editor_property('Difficulty', d); gen.set_editor_property('PuzzleType', t); gen.call_method('GenerateRoom', (seed,))
            acts = AS.get_all_level_actors()
            box = [a for a in acts if a.get_class().get_name() == 'BP_LockBox_C'][0]
            keys = [(k.get_attach_parent_actor().get_actor_label() if k.get_attach_parent_actor() else None) for k in acts if k.get_class().get_name() == 'BP_Key_C']
            print('D%d T%d s%d %04d' % (d, t, seed, gen.get_editor_property('CurrentCode')), [txt(n) for n in acts if n.get_class().get_name() == 'BP_Note_C'], 'key@', keys, 'boxHidden', box.is_hidden_ed() if hasattr(box,'is_hidden_ed') else box.get_editor_property('hidden'))
gen.set_editor_property('PuzzleType', 0); gen.set_editor_property('Difficulty', 0)
