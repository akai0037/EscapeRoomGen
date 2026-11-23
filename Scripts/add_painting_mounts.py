"""One-time setup: make the painting a piece of furniture.

Each painting hangs on an invisible 'Painting_Mount_<n>' actor tagged Furniture, so GenerateRoom shuffles it into a
wall slot like any other furniture (the painting sits above the slot, flat on the wall). Painting_Mount_1 carries the
original painting and the Hard-mode poster spots (on the painting / on the wall behind it). Mounts 2 and 3 carry
plain copies of the painting (they slide aside too, but hide nothing). er_layout decides which mounts are used."""
import unreal

A = unreal.AttachmentRule.KEEP_WORLD
D = unreal.DetachmentRule.KEEP_WORLD
actor_sys = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)


def labels():
    return {a.get_actor_label(): a for a in actor_sys.get_all_level_actors()}


def kids(actor):
    return [a for a in actor_sys.get_all_level_actors() if a.get_attach_parent_actor() == actor]


def movable(actor):
    if actor.root_component:
        actor.root_component.set_mobility(unreal.ComponentMobility.MOVABLE)


def drawer_comp(painting):
    return [c for c in painting.get_components_by_class(unreal.SceneComponent) if c.get_name() == "Drawer"][0]


def xf(x, y, z, yaw=0.0, pitch=0.0):
    return unreal.Transform(unreal.Vector(x, y, z), unreal.Rotator(roll=0, pitch=pitch, yaw=yaw), unreal.Vector(1, 1, 1))


def make_mount(name, folder):
    m = actor_sys.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(0, 0, 0))
    m.set_actor_label(name)
    m.set_folder_path(folder)
    smc = m.static_mesh_component
    smc.set_mobility(unreal.ComponentMobility.MOVABLE)
    smc.set_collision_profile_name("NoCollision")
    m.tags = [unreal.Name("Furniture")]
    return m


L = labels()
painting = L["BP_Painting"]
hidden = L["Spot_PosterHidden"]
folder = painting.get_folder_path()
HW = 400.0          # build everything against a back wall at x = -400, then attach (only relative offsets matter)
MOUNT = xf(-(HW - 25), 0, 0)                     # a back-wall furniture slot
PAINT = xf(-(HW - 8), -27, 108, yaw=90)          # painting: frame centred over the slot, flat on the wall
HIDE = xf(-(HW - 1), 0, 170, pitch=-90)          # wall spot behind the painting

if "Painting_Mount_1" in L:
    print("PMT already set up")
else:
    for a in [painting, hidden]:
        if a.get_attach_parent_actor():
            a.detach_from_actor(D, D, D)
    for a in [painting, hidden] + kids(painting):
        movable(a)
    m1 = make_mount("Painting_Mount_1", folder)
    m1.set_actor_transform(MOUNT, False, True)
    painting.set_actor_transform(PAINT, False, True)       # frame / canvas / Spot_Poster ride along
    hidden.set_actor_transform(HIDE, False, True)
    painting.attach_to_actor(m1, unreal.Name(), A, A, A, False)
    hidden.attach_to_actor(m1, unreal.Name(), A, A, A, False)

    plain = [painting] + [k for k in kids(painting) if not any(str(t).startswith("PosterSpot") for t in k.tags)]
    for n in (2, 3):
        m = make_mount("Painting_Mount_%d" % n, folder)
        m.set_actor_transform(MOUNT, False, True)
        copies = actor_sys.duplicate_actors(plain, None, unreal.Vector(0, 0, 0))
        cp = copies[0]
        cp.set_actor_label("BP_Painting_%d" % n)
        for orig, c in zip(plain, copies):
            c.set_folder_path(orig.get_folder_path())
            movable(c)
            if c is not cp:
                c.set_actor_label("%s_%d" % (orig.get_actor_label(), n))
                if c.get_attach_parent_actor():
                    c.detach_from_actor(D, D, D)
                c.attach_to_component(drawer_comp(cp), unreal.Name(), A, A, A, False)
        if cp.get_attach_parent_actor():
            cp.detach_from_actor(D, D, D)
        cp.attach_to_actor(m, unreal.Name(), A, A, A, False)
    print("PMT created mounts")

L = labels()
for n in (1, 2, 3):
    m = L["Painting_Mount_%d" % n]
    tree = []
    for k in kids(m):
        tree.append(k.get_actor_label() + "[" + ",".join(c.get_actor_label() for c in kids(k)) + "]")
    print("PMT", m.get_actor_label(), [str(t) for t in m.tags], tree)
