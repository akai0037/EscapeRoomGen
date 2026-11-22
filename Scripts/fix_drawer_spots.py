"""Attach each drawer's clue spot to the sliding 'Drawer' component so the
note moves out with the drawer when it opens. Keeps world position, and uses
absolute scale so the note is not squashed by the thin front-panel mesh."""
import unreal

eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
A = {a.get_actor_label(): a for a in eas.get_all_level_actors()}
K = unreal.AttachmentRule.KEEP_WORLD
for drawer, spot in [("BP_Drawer_1", "Spot_Drawer1"), ("BP_Drawer_2", "Spot_Drawer2")]:
    d, s = A[drawer], A[spot]
    comp = [c for c in d.get_components_by_class(unreal.SceneComponent) if c.get_name() == "Drawer"][0]
    r = s.root_component
    loc = s.get_actor_location()
    s.modify(); r.modify()
    r.attach_to_component(comp, "", K, K, K, False)
    r.set_absolute(False, False, True)
    r.set_world_scale3d(unreal.Vector(1, 1, 1))
    r.set_world_location(loc, False, False)
    print("FIX", spot, r.get_attach_parent().get_name(), s.get_actor_location(), s.get_actor_scale3d())
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
