"""Second step for the sliding painting: slide distance, movable frame/canvas, attach them."""
import unreal
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
f = lambda v: '(%.1f,%.1f,%.1f)' % (v.x, v.y, v.z)
bp = unreal.load_asset('/Game/EscapeRoom/Blueprints/BP_Painting')
cdo = unreal.get_default_object(bp.generated_class())
cdo.set_editor_property('OpenDistance', 90.0)        # BP adds this to the closed X (27): slides 90 cm along the wall
unreal.BlueprintEditorLibrary.compile_blueprint(bp)
unreal.EditorAssetLibrary.save_loaded_asset(bp)
L = {a.get_actor_label(): a for a in EAS.get_all_level_actors()}
painting = L['BP_Painting']
for c in painting.get_components_by_class(unreal.SceneComponent):
    print('APF comp', c.get_name(), type(c).__name__, f(c.get_world_location()), f(c.get_world_scale()))
moving = [c for c in painting.get_components_by_class(unreal.StaticMeshComponent) if c.get_name() == 'Drawer'][0]
for lab in ('Painting_Frame', 'Painting_Canvas', 'Spot_Poster'):
    a = L[lab]
    a.root_component.set_mobility(unreal.ComponentMobility.MOVABLE)
    ok = a.attach_to_component(moving, unreal.Name(), unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, False)
    if lab.startswith('Painting'):
        a.set_actor_enable_collision(False)
    p = a.get_attach_parent_actor()
    print('APF attached', lab, ok, f(a.get_actor_location()), p and p.get_actor_label())
unreal.EditorLevelLibrary.save_current_level()
