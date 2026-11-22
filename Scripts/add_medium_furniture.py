"""Add Medium-difficulty furniture to Lvl_EscapeRoom.

Duplicates the drawer cabinet (to Slot_Back_B) and the shelf (to Slot_Right_A)
together with their clue spots. The new furniture is tagged 'Medium' so the
generator can hide it in Easy mode, and the new clue spots are tagged
'ClueSpotMedium' (instead of 'ClueSpot') so Easy never puts a note there.
Run once from the Unreal console:  py "<project>/Scripts/add_medium_furniture.py"
"""
import unreal

eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors = {a.get_actor_label(): a for a in eas.get_all_level_actors()}

if "BP_Drawer_2" in actors or "BP_Shelf_2" in actors:
    print("MED already added, skipping")
else:
    def clone(parent_label, child_labels, offset, new_parent, rename):
        group = [actors[parent_label]] + [actors[c] for c in child_labels]
        new = eas.duplicate_actors(group, None, offset)
        out = {}
        for old, dup in zip(group, new):
            out[old.get_actor_label()] = dup
        # make sure children stay attached to the new parent
        p = out[parent_label]
        p.set_actor_label(new_parent)
        p.tags = [unreal.Name("Furniture"), unreal.Name("Medium")]
        for c in child_labels:
            d = out[c]
            if d.get_attach_parent_actor() != p:
                d.attach_to_actor(p, "", unreal.AttachmentRule.KEEP_WORLD,
                                  unreal.AttachmentRule.KEEP_WORLD,
                                  unreal.AttachmentRule.KEEP_WORLD, False)
            d.set_actor_label(rename(c))
        return out

    d = clone("BP_Drawer_1", ["Spot_Drawer1"], unreal.Vector(0, 360, 0),
              "BP_Drawer_2", lambda n: "Spot_Drawer2")
    d["BP_Drawer_1"].tags = [unreal.Name("Furniture"), unreal.Name("Medium"), unreal.Name("Drawer2")]
    d["Spot_Drawer1"].tags = [unreal.Name("ClueSpotMedium"), unreal.Name("Drawer2")]

    s = clone("BP_Shelf_1", ["Spot_ShelfLow", "Spot_ShelfMid", "Spot_ShelfTop"],
              unreal.Vector(-300, 0, 0), "BP_Shelf_2",
              lambda n: n.replace("Spot_Shelf", "Spot_Shelf2"))
    for c in ["Spot_ShelfLow", "Spot_ShelfMid", "Spot_ShelfTop"]:
        s[c].tags = [unreal.Name("ClueSpotMedium"), unreal.Name("open")]

    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()

for a in eas.get_all_level_actors():
    if a.get_actor_label().startswith(("BP_Drawer", "BP_Shelf", "Spot_")):
        par = a.get_attach_parent_actor()
        print("MED", a.get_actor_label(), [str(t) for t in a.tags], a.get_actor_location(),
              par.get_actor_label() if par else "-")
