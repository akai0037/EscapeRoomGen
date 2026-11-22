"""Generate many seeds and check visible furniture never overlaps (2D bounding boxes, 2cm tolerance)."""
import unreal, er_tool
def visible(diff):
    return [a for a in er_tool.level_actors() if unreal.Name('Furniture') in a.tags and (diff >= 1 or unreal.Name('Medium') not in a.tags)]
bad = []
for diff in (0, 1):
    for seed in range(200):
        er_tool.generate(seed, diff)
        boxes = []
        for a in visible(diff):
            o, e = a.get_actor_bounds(True)
            boxes.append((a.get_actor_label(), o.x - e.x, o.x + e.x, o.y - e.y, o.y + e.y))
        for i in range(len(boxes)):
            for j in range(i + 1, len(boxes)):
                A, B = boxes[i], boxes[j]
                if A[1] < B[2] - 2 and B[1] < A[2] - 2 and A[3] < B[4] - 2 and B[3] < A[4] - 2:
                    bad.append((diff, seed, A[0], B[0]))
print('LAYOUT overlaps', len(bad), bad[:10])
er_tool.generate(0, 1)
for a in visible(1):
    o, e = a.get_actor_bounds(True)
    print('LAYOUT box', a.get_actor_label(), [round(v) for v in (o.x, o.y, e.x, e.y)])
