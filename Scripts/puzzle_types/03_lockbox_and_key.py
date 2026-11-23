close_tool()
EAL = unreal.EditorAssetLibrary
print([a for a in EAL.list_assets('/Game/EscapeRoom/Materials', recursive=True)])
SRC = '/Game/EscapeRoom/Blueprints/BP_Painting'
sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
SDL = unreal.SubobjectDataBlueprintFunctionLibrary
CUBE = unreal.load_asset('/Engine/BasicShapes/Cube.Cube')
def comps(b):
    out = {}
    for h in sds.k2_gather_subobject_data_for_blueprint(b):
        d = sds.k2_find_subobject_data_from_handle(h); o = SDL.get_object(d)
        if o: out[o.get_name().replace('_GEN_VARIABLE', '')] = (h, o)
    return out
def add_cube(b, name, loc, scale):
    c = comps(b)
    root = c['DefaultSceneRoot'][0]
    h, fail = sds.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=root, new_class=unreal.StaticMeshComponent, blueprint_context=b))
    print('add', name, fail)
    sds.rename_subobject_member_variable(b, h, unreal.Name(name))
    o = SDL.get_object(sds.k2_find_subobject_data_from_handle(h))
    o.set_editor_property('static_mesh', CUBE)
    o.set_editor_property('relative_location', unreal.Vector(*loc)); o.set_editor_property('relative_scale3d', unreal.Vector(*scale))
    return o
def make(dst):
    if EAL.does_asset_exist(dst): EAL.delete_asset(dst)
    return EAL.duplicate_asset(SRC, dst)

# ================= BP_LockBox: a box whose lid slides off only after the key was found
box = make('/Game/EscapeRoom/Blueprints/BP_LockBox')
c = comps(box)
lid = c['Drawer'][1]
lid.set_editor_property('relative_location', unreal.Vector(0, 0, 33)); lid.set_editor_property('relative_scale3d', unreal.Vector(0.64, 0.44, 0.04))
add_cube(box, 'Body', (0, 0, 15.5), (0.6, 0.4, 0.31))
ed = G.get_graph_editor_by_name(box, 'EventGraph')
N = lambda nm: node(ed, nm)
setv(N('K2Node_CallFunction_2'), 'A', 0)            # lid starts at X = 0
setv(N('K2Node_PromotableOperator_0'), 'B', 0)      # ... and slides OpenDistance forward
setv(N('K2Node_CallFunction_3'), 'Z', 33)           # on top of the box
boolT = L.get_basic_type_by_name('bool')
ed.add_member_variable('Unlocked', boolT, 'false')
ev = N('K2Node_Event_3')
br = ed.add_branch_node(); L.set_node_pos(br, unreal.IntPoint(L.get_node_pos(ev).x + 250, L.get_node_pos(ev).y + 200))
gu = ed.add_get_member_variable_node('Unlocked'); L.set_node_pos(gu, unreal.IntPoint(L.get_node_pos(ev).x + 50, L.get_node_pos(ev).y + 320))
PL.break_pin_links(pin(ev, 'then')); link(ev, 'then', br, 'execute'); link(gu, 'Unlocked', br, 'Condition')
link(br, 'then', N('K2Node_VariableSet_0'), 'execute')
ps = ed.add_call_function_node('/Script/Engine.KismetSystemLibrary:PrintString'); L.set_node_pos(ps, unreal.IntPoint(L.get_node_pos(br).x + 250, L.get_node_pos(br).y + 200))
setv(ps, 'InString', "It's locked. Find the key.")
link(br, 'else', ps, 'execute')
L.compile_blueprint(box)
# Unlock(): called by the key
fe = G.create_and_edit_function_graph(box, 'Unlock')
s = fe.add_set_member_variable_node('Unlocked'); setv(s, 'Unlocked', 'true')
link(PL.get_owning_node(fe.find_graph_entry_pin()), 'then', s, 'execute')
# ResetBox(): locked, lid closed (called by the generator for every new room)
fe = G.create_and_edit_function_graph(box, 'ResetBox')
s1 = fe.add_set_member_variable_node('Unlocked'); setv(s1, 'Unlocked', 'false')
s2 = fe.add_set_member_variable_node('IsOpen'); setv(s2, 'IsOpen', 'false')
tl = fe.add_get_member_variable_node('TL_Open')
nt = fe.add_call_function_node('/Script/Engine.TimelineComponent:SetNewTime'); link(tl, 'TL_Open', nt, 'self'); setv(nt, 'NewTime', 0)
gd = fe.add_get_member_variable_node('Drawer')
rl = fe.add_call_function_node('/Script/Engine.SceneComponent:K2_SetRelativeLocation'); link(gd, 'Drawer', rl, 'self'); setv(rl, 'NewLocation', '0, 0, 33')
en = PL.get_owning_node(fe.find_graph_entry_pin())
link(en, 'then', s1, 'execute'); link(s1, 'then', s2, 'execute'); link(s2, 'then', nt, 'execute'); link(nt, 'then', rl, 'execute')
for i, n in enumerate([s1, s2, tl, nt, gd, rl]): L.set_node_pos(n, unreal.IntPoint(250 + 250 * i, 0 if i % 2 == 0 else 150))
L.compile_blueprint(box)
unreal.get_default_object(box.generated_class()).set_editor_property('OpenDistance', 55.0)
print('box errors', [str(L.get_node_title(n)) for g in ['EventGraph', 'Unlock', 'ResetBox'] for n in G.get_graph_editor_by_name(box, g).list_nodes_with_errors()])

# ================= BP_Key: pick it up with E -> unlocks the box
key = make('/Game/EscapeRoom/Blueprints/BP_Key')
c = comps(key)
bar = c['Drawer'][1]
bar.set_editor_property('relative_location', unreal.Vector(4, 0, 1.2)); bar.set_editor_property('relative_scale3d', unreal.Vector(0.16, 0.035, 0.02))
add_cube(key, 'Head', (-7, 0, 1.2), (0.07, 0.07, 0.022))
add_cube(key, 'Tooth', (10, 2.5, 1.2), (0.03, 0.03, 0.02))
ed = G.get_graph_editor_by_name(key, 'EventGraph')
ev = [n for n in ed.list_all_nodes() if 'Interact' in str(L.get_node_title(n))][0]
ed.remove_nodes([n for n in ed.list_all_nodes() if n.get_class().get_name() not in ('K2Node_Event',)])
ga = ed.add_call_function_node('/Script/Engine.GameplayStatics:GetActorOfClass')
setv(ga, 'ActorClass', '/Game/EscapeRoom/Blueprints/BP_LockBox.BP_LockBox_C')
un = ed.add_call_function_node('/Game/EscapeRoom/Blueprints/BP_LockBox.BP_LockBox_C:Unlock')
ps = ed.add_call_function_node('/Script/Engine.KismetSystemLibrary:PrintString'); setv(ps, 'InString', 'You found a key! Now open the box.')
de = ed.add_call_function_node('/Script/Engine.Actor:K2_DestroyActor')
print([k for k in pins(ga)], [k for k in pins(un)])
link(ev, 'then', ga, 'execute') if 'execute' in pins(ga) else None
link(ga, 'ReturnValue', un, 'self')
link(ga if 'then' in pins(ga) else ev, 'then', un, 'execute'); link(un, 'then', ps, 'execute'); link(ps, 'then', de, 'execute')
for i, n in enumerate([ga, un, ps, de]): L.set_node_pos(n, unreal.IntPoint(L.get_node_pos(ev).x + 300 + 300 * i, L.get_node_pos(ev).y))
L.compile_blueprint(key)
print('key errors', [str(L.get_node_title(n)) for n in ed.list_nodes_with_errors()])
for p in ['/Game/EscapeRoom/Blueprints/BP_LockBox', '/Game/EscapeRoom/Blueprints/BP_Key']: print('save', p, EAL.save_asset(p, False))
