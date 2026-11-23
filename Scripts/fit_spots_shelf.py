"""Clue spots for the Fab bookcase (NeoGothicBookcase), in the bookcase's own frame:
the open ledge in front of the glass, and two shelves behind the glass doors."""
import unreal
es = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
LOCAL = {'Low': (12, -35, 82.5), 'Mid': (-13, 35, 133.5), 'Top': (-13, 0, 182.5)}
for spot in es.get_all_level_actors():
    piece = spot.get_attach_parent_actor()
    if piece is None or piece.get_class().get_name() != 'BP_Shelf_C':
        continue
    lab = spot.get_actor_label()
    key = next((k for k in LOCAL if k in lab), None)
    if not key:
        continue
    loc = piece.get_actor_transform().transform_location(unreal.Vector(*LOCAL[key]))
    spot.set_actor_location(loc, False, True)
    print('FITS', lab, piece.get_actor_label(), round(loc.z, 1))
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
