"""Hard mode: add the spot where the symbol-order poster appears (on the painting on the back wall)."""
import unreal
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in EAS.get_all_level_actors():
    if a.get_actor_label() in ('PosterTest', 'Spot_Poster'):
        a.destroy_actor()
cls = unreal.load_class(None, '/Game/EscapeRoom/Blueprints/BP_ClueSpot.BP_ClueSpot_C')
spot = EAS.spawn_actor_from_class(cls, unreal.Vector(-393, 0, 170), unreal.Rotator(roll=0, pitch=-90, yaw=0))
spot.set_actor_label('Spot_Poster')
spot.tags = [unreal.Name('PosterSpot')]
spot.set_folder_path('ER/Interactive')
unreal.EditorLevelLibrary.save_current_level()
print('APS spot', spot.get_actor_location(), spot.get_actor_rotation(), spot.tags)
