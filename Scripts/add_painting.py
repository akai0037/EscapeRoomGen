"""Make the back-wall painting slide aside when the player presses E (BP_Painting),
and add a second poster spot hidden behind it (Hard mode picks one of the two per seed)."""
import unreal
EAL = unreal.EditorAssetLibrary
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
SDL = unreal.SubobjectDataBlueprintFunctionLibrary
f = lambda v: '(%.1f,%.1f,%.1f)' % (v.x, v.y, v.z)
SRC, DST = '/Game/EscapeRoom/Blueprints/BP_Drawer', '/Game/EscapeRoom/Blueprints/BP_Painting'

# 1. BP_Painting = BP_Drawer's slide logic (Interact -> timeline -> move the 'Drawer' part along X) without the cabinet
if not EAL.does_asset_exist(DST):
    EAL.duplicate_asset(SRC, DST)
bp = unreal.load_asset(DST)
sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
handles = sds.k2_gather_subobject_data_for_blueprint(bp)
by_name, drop = {}, []
for h in handles:
    d = SDL.get_data(h)
    nm = str(SDL.get_variable_name(d))
    by_name[nm] = h
    if nm.startswith(('Cabinet', 'Cab_', 'Drawer_')):
        drop.append(h)
print('AP components', list(by_name), 'dropping', len(drop))
if drop:
    print('AP deleted', sds.delete_subobjects(handles[0], drop, bp))
panel = SDL.get_object(SDL.get_data(by_name['Drawer']))
print('AP panel before', panel.get_name(), f(panel.get_editor_property('relative_location')), f(panel.get_editor_property('relative_scale3d')))
panel.set_editor_property('relative_scale3d', unreal.Vector(0.9, 0.04, 0.7))   # invisible box the size of the frame
panel.set_editor_property('hidden_in_game', True)
unreal.BlueprintEditorLibrary.compile_blueprint(bp)
cdo = unreal.get_default_object(bp.generated_class())
print('AP OpenDistance was', cdo.get_editor_property('OpenDistance'))
cdo.set_editor_property('OpenDistance', 117.0)        # closed at X=27, slides 90 cm along the wall when opened
unreal.BlueprintEditorLibrary.compile_blueprint(bp)
EAL.save_loaded_asset(bp)

# 2. place it over the painting and hang the frame, canvas and front poster spot on its moving part
for a in EAS.get_all_level_actors():
    if a.get_actor_label() in ('BP_Painting', 'Spot_PosterHidden'):
        a.destroy_actor()
L = {a.get_actor_label(): a for a in EAS.get_all_level_actors()}
painting = EAS.spawn_actor_from_class(bp.generated_class(), unreal.Vector(-392, -27, 108), unreal.Rotator(roll=0, pitch=0, yaw=90))
painting.set_actor_label('BP_Painting')
painting.set_folder_path('ER/Interactive')
moving = [c for c in painting.get_components_by_class(unreal.StaticMeshComponent) if c.get_name() == 'Drawer'][0]
print('AP moving part at', f(moving.get_world_location()))
for lab in ('Painting_Frame', 'Painting_Canvas', 'Spot_Poster'):
    a = L[lab]
    a.attach_to_component(moving, unreal.Name(), unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, False)
    if lab.startswith('Painting'):
        a.set_actor_enable_collision(False)      # so the E trace hits BP_Painting, not the frame
    print('AP attached', lab, f(a.get_actor_location()), a.get_attach_parent_actor().get_actor_label())

# 3. a second poster spot on the wall behind the painting
cls = unreal.load_class(None, '/Game/EscapeRoom/Blueprints/BP_ClueSpot.BP_ClueSpot_C')
hidden = EAS.spawn_actor_from_class(cls, unreal.Vector(-399, 0, 170), unreal.Rotator(roll=0, pitch=-90, yaw=0))
hidden.set_actor_label('Spot_PosterHidden')
hidden.tags = [unreal.Name('PosterSpot')]
hidden.set_folder_path('ER/Interactive')
unreal.EditorLevelLibrary.save_current_level()
print('AP done', f(hidden.get_actor_location()))
