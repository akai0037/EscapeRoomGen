close_tool()
ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
if ues.get_game_world(): print('PIE running - stop it first'); raise SystemExit
title = lambda n: str(L.get_node_title(n)).replace('\n', ' ')
e = G.get_graph_editor_by_name(bp, 'ClueText')
nodes = e.list_all_nodes()
en = [n for n in nodes if n.get_class().get_name() == 'K2Node_FunctionEntry'][0]
br = [n for n in nodes if title(n) == 'Branch'][0]
r1 = PL.get_owning_node(list(PL.list_connected_pins(pin(br, 'then')))[0])
# colour puzzle: the note shows only the digits; its colour (ClueColor) tells you where they go
br2 = e.add_branch_node(); r3 = e.add_return_node()
pt = e.add_get_member_variable_node('PuzzleType')
eq = e.add_call_function_node('/Script/Engine.KismetMathLibrary:EqualEqual_IntInt'); link(pt, 'PuzzleType', eq, 'A'); setv(eq, 'B', 2)
link(eq, 'ReturnValue', br2, 'Condition')
PL.break_pin_links(pin(br, 'then')); link(br, 'then', br2, 'execute')
link(br2, 'then', r3, 'execute'); link(en, 'Piece', r3, 'Out'); link(br2, 'else', r1, 'execute')
p = L.get_node_pos(br)
for n, dx, dy in [(br2, 250, -250), (pt, 0, -400), (eq, 200, -400), (r3, 1100, -300)]: L.set_node_pos(n, unreal.IntPoint(p.x + dx, p.y + dy))
L.compile_blueprint(bp)
print('errors', [title(n) for n in e.list_nodes_with_errors()])
AS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
gen = [a for a in AS.get_all_level_actors() if a.get_class().get_name() == 'BP_RoomGenerator_C'][0]
for t in range(4):
    gen.set_editor_property('PuzzleType', t)
    print(t, [gen.call_method('ClueText', (i, pc, '# @ & %')) for i, pc in [(0, '26'), (1, '18')]])
print('save', unreal.EditorAssetLibrary.save_asset(BP_PATH, False))
