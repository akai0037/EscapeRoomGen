"""Put the drawer clue spots back on the drawer floor (they had snapped onto the drawer's front panel).
The spot stays attached to the sliding 'Drawer' component so the note moves with the drawer."""
import unreal
f = lambda v: '(%d,%d,%d)' % (v.x, v.y, v.z)
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
    if a.get_actor_label() not in ('Spot_Drawer1', 'Spot_Drawer2'):
        continue
    root = a.root_component
    parent = root.get_attach_parent()
    print('FDS2 before', a.get_actor_label(), parent and parent.get_name(), f(a.get_actor_location()))
    # Drawer component is scaled (0.06, ~1, 0.24), so -400 local = 24 cm behind the front, -29 = just above the bottom board
    root.set_editor_property('relative_location', unreal.Vector(-400, 0, -29))
    root.set_editor_property('relative_rotation', unreal.Rotator(0, 0, 0))
    print('FDS2 after', a.get_actor_label(), f(a.get_actor_location()), f(a.get_actor_scale3d()))
unreal.EditorLevelLibrary.save_current_level()
import er_tool
for seed in range(40):
    code, notes, spots = er_tool.generate(seed, 2)
    for n, s in zip(notes, spots):
        if 'Drawer' in s.get_actor_label():
            d = s.get_attach_parent_actor()
            print('FDS2 seed', seed, er_tool.note_text(n), s.get_actor_label(), 'note', f(n.get_actor_location()),
                  'drawer bottom', f(d.get_component_by_class(unreal.StaticMeshComponent).get_world_location()) if False else '')
er_tool.clear_notes()
