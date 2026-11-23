"""After swapping in Fab furniture: drop every clue spot onto a real surface of its new model
(trace straight down from above the spot's spot in the furniture's own frame)."""
import unreal
es = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
# spot name -> (local x, local y, start height): the first surface below the start height is used
PLAN = {'ShelfLow': (12, -35, 130), 'ShelfMid': (12, 35, 185), 'ShelfTop': (12, 0, 235),
        'Shelf2Low': (12, -35, 130), 'Shelf2Mid': (12, 35, 185), 'Shelf2Top': (12, 0, 235),
        'DeskTop': (10, -35, 150), 'ChairSeat': (80, 0, 70)}


def surface(piece, lx, ly, top):
    xf = piece.get_actor_transform()
    start = xf.transform_location(unreal.Vector(lx, ly, top))
    end = xf.transform_location(unreal.Vector(lx, ly, 1))
    ignore = [a for a in es.get_all_level_actors() if a.get_class().get_name() in ('BP_ClueSpot_C', 'BP_Note_C')]
    hit = unreal.SystemLibrary.line_trace_single(world, start, end, unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, ignore,
                                                  unreal.DrawDebugTrace.NONE, True)
    if hit is None:
        return None
    r = hit.to_tuple()
    hit_ok, loc, actor = r[0], r[4], r[9]   # blocking hit, location, hit actor
    if not hit_ok or actor != piece:
        return None
    return loc


for spot in es.get_all_level_actors():
    piece = spot.get_attach_parent_actor()
    if piece is None or spot.get_class().get_name() != 'BP_ClueSpot_C':
        continue
    key = spot.get_actor_label().replace('Spot_', '').rsplit('_', 1)[0] if spot.get_actor_label().count('_') > 1 else spot.get_actor_label().replace('Spot_', '')
    if key not in PLAN:
        continue
    lx, ly, top = PLAN[key]
    loc = surface(piece, lx, ly, top)
    if loc is None:
        print('FIT miss', spot.get_actor_label(), piece.get_actor_label())
        continue
    spot.set_actor_location(loc + unreal.Vector(0, 0, 0.5), False, True)
    print('FIT', spot.get_actor_label(), 'on', piece.get_actor_label(), 'z', round(loc.z, 1))
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
