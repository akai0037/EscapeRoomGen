close_tool()
pie = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
if pie:
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play(); print('ended PIE')
EAL = unreal.EditorAssetLibrary
# why does the note show through the lid? look at the note materials
n_cls = EAL.load_blueprint_class('/Game/EscapeRoom/Blueprints/BP_Note')
AS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
tmp = AS.spawn_actor_from_class(n_cls, unreal.Vector(0, 0, -5000))
for c in tmp.get_components_by_class(unreal.PrimitiveComponent):
    try:
        for i in range(c.get_num_materials()):
            m = c.get_material(i); base = m.get_base_material() if m else None
            print(c.get_name(), m.get_name() if m else None, 'depthtest off' if base and base.get_editor_property('disable_depth_test') else 'depth ok', base.get_editor_property('blend_mode') if base else '')
    except Exception as e: print(c.get_name(), e)
AS.destroy_actor(tmp)
title = lambda n: str(L.get_node_title(n)).replace('\n', ' ')
objT = L.get_object_reference_type(unreal.Actor.static_class())
# ---- BP_LockBox: remember the hidden note, show it when the lid opens
box = unreal.load_asset('/Game/EscapeRoom/Blueprints/BP_LockBox')
ed = G.get_graph_editor_by_name(box, 'EventGraph')
if 'HiddenNote' not in [str(v) for v in L.list_member_variable_names(box)]:
    ed.add_member_variable('HiddenNote', objT, '')
L.compile_blueprint(box)
br = [n for n in ed.list_all_nodes() if title(n) == 'Branch' and any('Unlocked' in title(PL.get_owning_node(q)) for q in PL.list_connected_pins(pin(n, 'Condition')))][0]
nxt = list(PL.list_connected_pins(pin(br, 'then')))
sh = ed.add_call_function_node('/Script/Engine.Actor:SetActorHiddenInGame'); setv(sh, 'bNewHidden', 'false')
gh = ed.add_get_member_variable_node('HiddenNote'); link(gh, 'HiddenNote', sh, 'self')
p = L.get_node_pos(br); L.set_node_pos(sh, unreal.IntPoint(p.x + 250, p.y - 150)); L.set_node_pos(gh, unreal.IntPoint(p.x + 50, p.y - 50))
PL.break_pin_links(pin(br, 'then')); link(br, 'then', sh, 'execute')
for q in nxt: PL.try_create_connection(pin(sh, 'then'), q)
L.compile_blueprint(box)
print('box errors', [title(n) for n in ed.list_nodes_with_errors()], EAL.save_asset('/Game/EscapeRoom/Blueprints/BP_LockBox', False))
# ---- generator: hide the boxed note and tell the box about it
e = G.get_graph_editor_by_name(bp, 'ApplyKeyPuzzle')
nodes = e.list_all_nodes()
sp = [n for n in nodes if 'AttachParent' in title(n) or 'Attach Parent' in title(n)][0]
at1 = [n for n in nodes if title(n) == 'Attach Actor To Actor' and not any(PL.get_owning_node(q).get_class().get_name() == 'K2Node_VariableGet' for q in PL.list_connected_pins(pin(n, 'ParentActor')))][0]
ag_note = PL.get_owning_node(list(PL.list_connected_pins(pin(at1, 'self')))[0])
gb = [n for n in nodes if title(n) == 'GetActorOfClass'][0]
nxt = list(PL.list_connected_pins(pin(at1, 'then')))
hn = e.add_call_function_node('/Script/Engine.Actor:SetActorHiddenInGame'); setv(hn, 'bNewHidden', 'true')
link(ag_note, list(pins(ag_note))[2] if ag_note.get_class().get_name() == 'K2Node_CallArrayFunction' else 'ReturnValue', hn, 'self')
sv = e.add_set_member_variable_node('HiddenNote', '/Game/EscapeRoom/Blueprints/BP_LockBox.BP_LockBox_C')
print('set pins', list(pins(sv)))
link(gb, 'ReturnValue', sv, 'self'); link(ag_note, list(pins(ag_note))[2], sv, 'HiddenNote')
p = L.get_node_pos(at1); L.set_node_pos(hn, unreal.IntPoint(p.x + 150, p.y + 250)); L.set_node_pos(sv, unreal.IntPoint(p.x + 450, p.y + 250))
PL.break_pin_links(pin(at1, 'then')); link(at1, 'then', hn, 'execute'); link(hn, 'then', sv, 'execute')
for q in nxt: PL.try_create_connection(pin(sv, 'then'), q)
L.compile_blueprint(bp)
print('gen errors', [title(n) for n in e.list_nodes_with_errors()], EAL.save_asset(BP_PATH, False))
gen = [a for a in AS.get_all_level_actors() if a.get_class().get_name() == 'BP_RoomGenerator_C'][0]
gen.set_editor_property('Difficulty', 1); gen.set_editor_property('PuzzleType', 3); gen.call_method('GenerateRoom', (4,))
acts = AS.get_all_level_actors()
b = [a for a in acts if a.get_class().get_name() == 'BP_LockBox_C'][0]
hn_ = b.get_editor_property('HiddenNote')
print('box.HiddenNote', hn_.get_name() if hn_ else None, 'hidden', hn_.get_editor_property('hidden') if hn_ else None)
print('others hidden', [a.get_editor_property('hidden') for a in acts if a.get_class().get_name() == 'BP_Note_C' and a != hn_])
