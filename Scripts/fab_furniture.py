"""Dress the furniture Blueprints with Fab models (the old cube parts stay, hidden and without collision).
Run with the Room Generator panel CLOSED (compiling Blueprints while it is open crashes the editor)."""
import unreal
EAL = unreal.EditorAssetLibrary
SDL = unreal.SubobjectDataBlueprintFunctionLibrary
sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
UB = '/Game/UnrealBucket/Library/ArchViz/'
BP = '/Game/EscapeRoom/Blueprints/'

# mesh, parent component ('' = root), location, yaw, scale
PLAN = {
    'BP_Shelf': [('Fab_Bookcase', UB + 'NeoGothicBookcase/SM_NeoGothicBookcase', '', (-27, 0, 0), -90, 1.0)],
    'BP_DeskSet': [('Fab_Desk', UB + 'ClassicConsole/SM_ClassicConsole', '', (5, 0, 0), -90, 1.0),
                   ('Fab_Chair', UB + 'Chair_02/SM_Chair', '', (80, 0, 0), 90, 1.0)],
    'BP_Drawer': [('Fab_Nightstand', UB + 'Nightstand_01/SM_Nightstand_01_Base', '', (6, 0, 0), -90, 1.0),
                  ('Fab_NightDrawer', UB + 'Nightstand_01/SM_Nightstand_01_Drawer_A', 'Drawer', (-5, 0, -10), -90, 1.0)],
}


def obj(h):
    d = SDL.get_data(h)
    return SDL.get_associated_object(d) if hasattr(SDL, 'get_associated_object') else SDL.get_object(d)


for name, parts in PLAN.items():
    path = BP + name
    if not EAL.does_asset_exist('/Game/EscapeRoom/Backup/%s_PreFab' % name):
        EAL.duplicate_asset(path, '/Game/EscapeRoom/Backup/%s_PreFab' % name)
    bp = unreal.load_asset(path)
    handles = sds.k2_gather_subobject_data_for_blueprint(bp)
    by = {str(SDL.get_variable_name(SDL.get_data(h))): h for h in handles}
    for nm, h in by.items():                       # hide the cube look
        o = obj(h)
        if isinstance(o, unreal.StaticMeshComponent) and not nm.startswith('Fab_'):
            o.set_editor_property('visible', False)
            if name != 'BP_Drawer' or nm not in ('Drawer',):
                o.set_editor_property('collision_profile_name', 'NoCollision')
    for comp, mesh, parent, loc, yaw, sc in parts:
        if comp in by:
            o = obj(by[comp])
        else:
            p = unreal.AddNewSubobjectParams(parent_handle=by[parent] if parent else handles[0], new_class=unreal.StaticMeshComponent, blueprint_context=bp)
            h, fail = sds.add_new_subobject(p)
            sds.rename_subobject(h, unreal.Text(comp))
            o = obj(h)
            by[comp] = h
        o.set_editor_property('static_mesh', unreal.load_asset(mesh))
        if parent:                                   # the sliding drawer part is scaled - keep the model's own size
            o.set_editor_property('absolute_scale', True)
            ps = obj(by[parent]).get_editor_property('relative_scale3d')
            loc = (loc[0] / ps.x, loc[1] / ps.y, loc[2] / ps.z)
        o.set_editor_property('relative_location', unreal.Vector(*loc))
        o.set_editor_property('relative_rotation', unreal.Rotator(roll=0, pitch=0, yaw=yaw))
        o.set_editor_property('relative_scale3d', unreal.Vector(sc, sc, sc))
        print('FAB', name, comp, mesh.split('/')[-1], loc)
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    print('FAB saved', name, EAL.save_loaded_asset(bp))
