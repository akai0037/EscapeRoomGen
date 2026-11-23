"""Go back to the white-box (grey cube) furniture: remove the Fab_* parts added by fab_furniture.py and restore the
cube parts' visibility/collision and the drawer slide distance from the backups made before the swap.
Run with the Room Generator panel CLOSED."""
import unreal
EAL = unreal.EditorAssetLibrary
SDL = unreal.SubobjectDataBlueprintFunctionLibrary
sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
es = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)


def obj(h):
    return SDL.get_associated_object(SDL.get_data(h))


def comps(bp):
    hs = sds.k2_gather_subobject_data_for_blueprint(bp)
    return hs, {str(SDL.get_variable_name(SDL.get_data(h))): h for h in hs}


for name in ('BP_Shelf', 'BP_DeskSet', 'BP_Drawer'):
    bp = unreal.load_asset('/Game/EscapeRoom/Blueprints/' + name)
    backup = unreal.load_asset('/Game/EscapeRoom/Backup/%s_PreFab' % name)
    hs, by = comps(bp)
    _, old = comps(backup)
    fab = [h for n, h in by.items() if n.startswith('Fab_')]
    if fab:
        print('RVT removed', name, sds.delete_subobjects(hs[0], fab, bp))
    for n, h in by.items():
        if n.startswith('Fab_') or n not in old:
            continue
        o, b = obj(h), obj(old[n])
        if isinstance(o, unreal.StaticMeshComponent):
            o.set_editor_property('visible', b.get_editor_property('visible'))
            o.set_collision_profile_name(b.get_collision_profile_name())
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    if name == 'BP_Drawer':
        unreal.get_default_object(bp.generated_class()).set_editor_property(
            'OpenDistance', unreal.get_default_object(backup.generated_class()).get_editor_property('OpenDistance'))
        unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    print('RVT saved', name, EAL.save_loaded_asset(bp))

# clue spots back to their white-box places, in each piece's own frame
LOCAL = {'ShelfLow': (-7, -30, 62), 'ShelfMid': (-7, 30, 117), 'ShelfTop': (-7, -10, 172),
         'Shelf2Low': (-7, -30, 62), 'Shelf2Mid': (-7, 30, 117), 'Shelf2Top': (-7, -10, 172),
         'DeskTop': (10, -35, 78), 'ChairSeat': (80, 0, 48)}
for spot in es.get_all_level_actors():
    piece = spot.get_attach_parent_actor()
    if piece is None or spot.get_class().get_name() != 'BP_ClueSpot_C':
        continue
    key = spot.get_actor_label().replace('Spot_', '')
    key = key.rsplit('_', 1)[0] if key not in LOCAL else key
    if key in LOCAL:
        spot.set_actor_location(piece.get_actor_transform().transform_location(unreal.Vector(*LOCAL[key])), False, True)
        print('RVT spot', spot.get_actor_label())
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
