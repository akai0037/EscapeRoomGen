"""
Room layout for the Escape Room Generator: room size and furniture count per difficulty.

The settings live in room_layout.json next to this file. apply_layout() turns them into:
  * BP_RoomGenerator.LayoutActors / LayoutTransforms - where every wall, the door, the painting and
    every furniture slot goes for each difficulty (GenerateRoom moves them at the start of a game)
  * tags the Blueprint reads for the chosen difficulty d:
      FurnitureSlot<d>  slots that exist in that room size
      Furniture<d>      furniture that is placed (the first N pieces of the pool, N = furniture count)
      ClueSpot<d>       clue spots on placed furniture (and on the floor)
  * extra furniture (copies of the shelf / drawer / desk, with their clue spots) and extra slots
    when a room needs more than the level has.

Paintings count as furniture: each hangs on an invisible Painting_Mount_<n> that is shuffled into a wall slot like
any other piece (the painting hangs above the slot). Mount 1 always comes first, so every room has the painting with
the Hard poster; mounts 2 and 3 join at pool positions 6 and 10. A mount that isn't used on a difficulty is parked
under the floor by the layout step (hiding an actor in game does not hide the painting attached to it).
"""
import json
import os

import unreal

HERE = os.path.dirname(os.path.abspath(__file__))
SETTINGS_FILE = os.path.join(HERE, "room_layout.json")
DIFFICULTIES = ["Easy", "Medium", "Hard"]
DEFAULTS = [{"width": 800, "depth": 600, "furniture": 3},
            {"width": 1000, "depth": 700, "furniture": 5},
            {"width": 1200, "depth": 800, "furniture": 7}]
LIMITS = {"width": (600, 2000), "depth": (500, 1600), "furniture": (1, 16)}
SLOT_SPACING = 300          # one furniture slot per 3 m of wall
WALL_GAP = 25               # furniture slot distance from the wall (cm)
CORNER = 70                 # side-wall slots start this far from the back wall (furniture there is ~60 cm deep)
POOL_ORDER = ["BP_DeskSet_1", "BP_Shelf_1", "BP_Drawer_1", "BP_Drawer_2", "BP_Shelf_2"]
PAINTINGS = ["Painting_Mount_1", "Painting_Mount_2", "Painting_Mount_3"]
PAINTING_AT = [0, 5, 9]     # where each painting joins the furniture pool (pool order = which pieces a count uses)
COPY_FROM = ["BP_Shelf_1", "BP_Drawer_1", "BP_DeskSet_1"]   # what extra furniture is copied from, in turn
PARKED = unreal.Vector(0, 0, -2000)                           # unused slots are parked under the floor

actor_sys = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)


# ---------------------------------------------------------------- settings
def load_settings():
    try:
        with open(SETTINGS_FILE) as f:
            data = json.load(f)
        return [dict(DEFAULTS[i], **data[i]) for i in range(3)]
    except Exception:
        return [dict(d) for d in DEFAULTS]


def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=2)


def clamp(key, value):
    lo, hi = LIMITS[key]
    return max(lo, min(hi, int(value)))


# ---------------------------------------------------------------- geometry
def xf(x, y, z, yaw=0.0, pitch=0.0, sx=1.0, sy=1.0, sz=1.0):
    return unreal.Transform(unreal.Vector(x, y, z), unreal.Rotator(roll=0, pitch=pitch, yaw=yaw), unreal.Vector(sx, sy, sz))


def room_parts(width, depth):
    """Transform of every room piece for an inner room of width (x) by depth (y), centred on the origin.
    With 800 x 600 this gives exactly the original hand-built room."""
    hw, hd = width / 2.0, depth / 2.0
    side = (hd + 20 - 50) / 100.0           # each front wall piece runs from the door gap (|y| = 50) to the corner
    return {
        "Floor": xf(0, 0, -10, sx=(width + 40) / 100.0, sy=(depth + 40) / 100.0, sz=0.2),
        "Ceiling": xf(0, 0, 310, sx=(width + 40) / 100.0, sy=(depth + 40) / 100.0, sz=0.2),
        "Wall_Back": xf(-(hw + 10), 0, 150, sx=0.2, sy=(depth + 40) / 100.0, sz=3),
        "Wall_Left": xf(0, hd + 10, 150, sx=width / 100.0, sy=0.2, sz=3),
        "Wall_Right": xf(0, -(hd + 10), 150, sx=width / 100.0, sy=0.2, sz=3),
        "Wall_Front_A": xf(hw + 10, -(hd + 70) / 2.0, 150, sx=0.2, sy=side, sz=3),
        "Wall_Front_B": xf(hw + 10, (hd + 70) / 2.0, 150, sx=0.2, sy=side, sz=3),
        "Wall_Front_Top": xf(hw + 10, 0, 255, sx=0.2, sy=1.0, sz=0.9),
        "Door_Frame_L": xf(hw - 2, -54, 105, sx=0.12, sy=0.08, sz=2.1),
        "Door_Frame_R": xf(hw - 2, 54, 105, sx=0.12, sy=0.08, sz=2.1),
        "Door_Frame_T": xf(hw - 2, 0, 214, sx=0.12, sy=1.16, sz=0.08),
        "BP_Door_1": xf(hw + 2, 0, 0),
        "Outside_Floor": xf(hw + 100, 0, -10, sx=1.8, sy=2.0, sz=0.2),
        "Outside_Light": xf(hw + 120, 0, 250),
        "Light_Ceiling": xf(0, 0, 270),
    }


def slot_spots(width, depth):
    """Furniture slots along the back wall and both side walls (the front wall has the door)."""
    hw, hd = width / 2.0, depth / 2.0
    out = []
    k = max(1, int(depth // SLOT_SPACING))
    for i in range(k):
        out.append(xf(-(hw - WALL_GAP), -hd + (i + 0.5) * depth / k, 0, yaw=0))
    # side walls: keep clear of the back corners, where a back-wall piece already reaches (CORNER cm)
    k = max(1, int(width // SLOT_SPACING))
    run = width - CORNER
    for i in range(k):
        out.append(xf(-hw + CORNER + (i + 0.5) * run / k, hd - WALL_GAP, 0, yaw=-90))
    for i in range(k):
        out.append(xf(-hw + CORNER + (i + 0.5) * run / k, -(hd - WALL_GAP), 0, yaw=90))
    return out


# ---------------------------------------------------------------- level helpers
def by_label():
    return {a.get_actor_label(): a for a in actor_sys.get_all_level_actors()}


def children_of(actor):
    return [a for a in actor_sys.get_all_level_actors() if a.get_attach_parent_actor() == actor]


def descendants(actor):
    out, todo = [], [actor]
    while todo:
        kids = children_of(todo.pop())
        out += kids
        todo += kids
    return out


def is_painting(actor):
    return actor.get_actor_label().startswith("Painting_Mount")


def with_paintings(furniture, mounts):
    pool = list(furniture)
    for at, m in zip(PAINTING_AT, mounts):
        if at <= len(pool):
            pool.insert(at, m)
    return pool


def set_tags(actor, keep_prefixes, add):
    """Replace the per-difficulty tags of an actor, keeping its other tags."""
    tags = [t for t in actor.tags if not any(str(t).startswith(p) for p in keep_prefixes)]
    actor.tags = tags + [unreal.Name(t) for t in add]


def furniture_pool(count_needed):
    """The furniture actors in placement order, copying pieces (with their clue spots) if there are too few."""
    labels = by_label()
    mounts = [labels[l] for l in PAINTINGS if l in labels]
    pool = [labels[l] for l in POOL_ORDER if l in labels]
    extra = sorted([a for a in actor_sys.get_all_level_actors()
                    if unreal.Name("Furniture") in a.tags and a not in pool and not is_painting(a)],
                   key=lambda a: a.get_actor_label())
    pool += extra
    i = 0
    while len(with_paintings(pool, mounts)) < count_needed:
        src = labels[COPY_FROM[i % len(COPY_FROM)]]
        group = [src] + children_of(src)
        copies = actor_sys.duplicate_actors(group, None, unreal.Vector(0, 0, 0))
        new_label = "%s_%d" % (src.get_actor_label().rsplit("_", 1)[0], len(pool) + 1)
        for orig, cp in zip(group, copies):
            cp.set_actor_label(new_label if orig == src else "%s_%d" % (orig.get_actor_label(), len(pool) + 1))
            cp.set_folder_path(orig.get_folder_path())
        pool.append(copies[0])
        i += 1
    return with_paintings(pool, mounts)


def slot_pool(count_needed):
    slots = sorted([a for a in actor_sys.get_all_level_actors() if unreal.Name("FurnitureSlot") in a.tags],
                   key=lambda a: a.get_actor_label())
    cls = unreal.load_class(None, "/Game/EscapeRoom/Blueprints/BP_FurnitureSlot.BP_FurnitureSlot_C")
    while len(slots) < count_needed:
        s = actor_sys.spawn_actor_from_class(cls, PARKED)
        s.set_actor_label("Slot_%02d" % (len(slots) + 1))
        s.set_folder_path("ER/Generator/FurnitureSlots")
        s.tags = [unreal.Name("FurnitureSlot")]
        slots.append(s)
    return slots


DRAWER_SPOT_LOCAL = unreal.Vector(3, 0, 55)   # on the floor of the (closed) drawer, in the cabinet's frame


def fix_drawer_spots():
    """Clue spots in drawers must ride on the sliding 'Drawer' part. Recompiling BP_Drawer re-attaches them to the
    cabinet root, so put them back inside the drawer and on the sliding part every time the layout is applied."""
    for spot in actor_sys.get_all_level_actors():
        piece = spot.get_attach_parent_actor()
        if piece is None or piece.get_class().get_name() != "BP_Drawer_C" or spot.get_class().get_name() != "BP_ClueSpot_C":
            continue
        slider = [c for c in piece.get_components_by_class(unreal.SceneComponent) if c.get_name() == "Drawer"][0]
        spot.detach_from_actor(unreal.DetachmentRule.KEEP_WORLD, unreal.DetachmentRule.KEEP_WORLD, unreal.DetachmentRule.KEEP_WORLD)
        spot.set_actor_location(piece.get_actor_transform().transform_location(DRAWER_SPOT_LOCAL), False, True)
        spot.attach_to_component(slider, unreal.Name(), unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD,
                                 unreal.AttachmentRule.KEEP_WORLD, False)


# Each painting, in its mount's frame (x = out of the wall, the mount sits 25 cm from the wall): the sliding box of
# BP_Painting is the frame; the canvas sits on its front; the poster spot sits on the canvas, facing the room.
PAINTING_PARTS = {
    "BP_Painting": (unreal.Vector(-17, -27, 108), unreal.Rotator(roll=0, pitch=0, yaw=90), unreal.Vector(1, 1, 1)),
    "Painting_Frame": (unreal.Vector(-17, 0, 170), unreal.Rotator(roll=0, pitch=0, yaw=90), unreal.Vector(0.9, 0.04, 0.7)),
    "Painting_Canvas": (unreal.Vector(-14.5, 0, 170), unreal.Rotator(roll=0, pitch=0, yaw=90), unreal.Vector(0.8, 0.01, 0.6)),
    "Spot_Poster": (unreal.Vector(-13.5, 0, 170), unreal.Rotator(roll=0, pitch=-90, yaw=0), unreal.Vector(1, 1, 1)),
}


def fix_paintings():
    """Re-hang every painting on its mount: frame, canvas and poster spot ride on the sliding 'Drawer' box.
    Recompiling BP_Painting can snap or re-attach them (like the drawer spots), so this runs on every Apply layout."""
    K, D = unreal.AttachmentRule.KEEP_WORLD, unreal.DetachmentRule.KEEP_WORLD
    labels = by_label()
    for name in PAINTINGS:
        mount = labels.get(name)
        if mount is None:
            continue
        mt = mount.get_actor_transform()
        paintings = [a for a in children_of(mount) if a.get_class().get_name() == "BP_Painting_C"]
        if not paintings:
            continue
        painting = paintings[0]
        parts = children_of(painting)

        def place(actor, key):
            loc, rot, scale = PAINTING_PARTS[key]
            world = unreal.MathLibrary.compose_transforms(unreal.Transform(loc, rot, scale), mt)
            actor.set_actor_transform(world, False, True)

        for p in parts:
            p.detach_from_actor(D, D, D)
        place(painting, "BP_Painting")
        slider = [c for c in painting.get_components_by_class(unreal.SceneComponent) if c.get_name() == "Drawer"][0]
        for p in parts:
            key = next((k for k in ("Painting_Frame", "Painting_Canvas", "Spot_Poster") if p.get_actor_label().startswith(k)), None)
            if key:
                p.root_component.set_mobility(unreal.ComponentMobility.MOVABLE)
                place(p, key)
            p.attach_to_component(slider, unreal.Name(), K, K, K, False)


# ---------------------------------------------------------------- apply
def apply_layout(settings=None):
    """Write the room sizes and furniture counts into the level. Returns a short report."""
    settings = settings or load_settings()
    settings = [{k: clamp(k, s[k]) for k in ("width", "depth", "furniture")} for s in settings]
    slots_per = [slot_spots(s["width"], s["depth"]) for s in settings]
    counts = [min(s["furniture"], len(slots_per[d])) for d, s in enumerate(settings)]
    pool = furniture_pool(max(counts))
    slots = slot_pool(max(len(sp) for sp in slots_per))

    # tags
    for i, piece in enumerate(pool):
        set_tags(piece, ["Furniture", "Medium"], ["Furniture"] + ["Furniture%d" % d for d in range(3) if i < counts[d]])
        piece.set_actor_hidden_in_game(False)
    mounts = [p for p in pool if is_painting(p)]
    for m in mounts:
        for a in [m] + descendants(m):
            if a.root_component:
                a.root_component.set_mobility(unreal.ComponentMobility.MOVABLE)
    placed = [set(pool[:counts[d]]) for d in range(3)]
    for spot in actor_sys.get_all_level_actors():
        if not any(str(t).startswith("ClueSpot") for t in spot.tags):
            continue
        parent = spot.get_attach_parent_actor()
        ok = [d for d in range(3) if parent is None or parent in placed[d]]
        set_tags(spot, ["ClueSpot"], ["ClueSpot"] + ["ClueSpot%d" % d for d in ok])
    for j, slot in enumerate(slots):
        set_tags(slot, ["FurnitureSlot"], ["FurnitureSlot"] + ["FurnitureSlot%d" % d for d in range(3) if j < len(slots_per[d])])

    # transforms per difficulty
    labels = by_label()
    parts = [room_parts(s["width"], s["depth"]) for s in settings]
    room_actors = [labels[l] for l in parts[0] if l in labels]
    for a in room_actors:
        if a.root_component:
            a.root_component.set_mobility(unreal.ComponentMobility.MOVABLE)   # walls move when the game starts
    layout_actors = room_actors + slots + mounts
    transforms = []
    for d in range(3):
        for a in room_actors:
            transforms.append(parts[d][a.get_actor_label()])
        for j in range(len(slots)):
            transforms.append(slots_per[d][j] if j < len(slots_per[d]) else xf(PARKED.x, PARKED.y, PARKED.z))
        for m in mounts:   # used: anywhere (the shuffle moves it into a slot); unused: parked under the floor
            used = unreal.Name("Furniture%d" % d) in m.tags
            transforms.append(slots_per[d][0] if used else xf(PARKED.x, PARKED.y, PARKED.z))
    fix_drawer_spots()
    fix_paintings()
    gen = [a for a in actor_sys.get_all_level_actors() if a.get_class().get_name() == "BP_RoomGenerator_C"][0]
    gen.set_editor_property("LayoutActors", layout_actors)
    gen.set_editor_property("LayoutTransforms", transforms)
    save_settings(settings)
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    lines = []
    for d, s in enumerate(settings):
        pics = sum(1 for i, p in enumerate(pool) if i < counts[d] and is_painting(p))
        line = "%s: %d x %d cm, %d furniture incl. %d painting%s (%d slots)" % (
            DIFFICULTIES[d], s["width"], s["depth"], counts[d], pics, "" if pics == 1 else "s", len(slots_per[d]))
        if s["furniture"] > counts[d]:
            line += "\n    asked for %d, only %d fit - make the room bigger for more" % (s["furniture"], counts[d])
        lines.append(line)
    return lines


def preview(difficulty):
    """Move the room to a difficulty's layout in the editor (GenerateRoom does the same in game)."""
    gen = [a for a in actor_sys.get_all_level_actors() if a.get_class().get_name() == "BP_RoomGenerator_C"][0]
    actors = gen.get_editor_property("LayoutActors")
    transforms = gen.get_editor_property("LayoutTransforms")
    n = len(actors)
    for i, a in enumerate(actors):
        if a and len(transforms) >= (difficulty + 1) * n:
            a.set_actor_transform(transforms[difficulty * n + i], False, True)
