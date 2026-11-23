"""
Escape Room Generator tool for Unreal Engine 5 (Python + PySide6).

Open it from the Unreal menu bar: Escape Room > Room Generator Tool,
or in the Python console:  import er_tool; er_tool.show()

What it does (all in the editor, no Play needed):
  Difficulty - Easy (one note, full code), Medium (extra furniture, code split over two notes)
               or Hard (extra furniture, four notes like "@ = 7" plus a symbol-order poster -
               on the painting or, on some seeds, behind it: slide the painting aside with E)
  Generate   - calls BP_RoomGenerator.GenerateRoom(seed) on the RoomGenerator in the level
  Clear      - removes every BP_Note from the level
  Focus      - selects the generated note and points the viewport camera at it
  Clue spots - lists every BP_ClueSpot, adds a new spot on top of the selected actor, deletes spots
  Batch test - generates seeds 0..N-1 at the chosen difficulty (furniture is shuffled into the
               FurnitureSlots by the seed too), checks no furniture overlaps, every room is solvable
               (right number of notes, on allowed spots, halves add up to the code) and reports
               where the clues landed
"""
import os
import sys
import random

import unreal

# PySide6 is installed next to this file in ./site-packages (outside the engine folder).
_HERE = os.path.dirname(os.path.abspath(__file__))
for _SITE in (os.path.join(_HERE, "site-packages"),
              os.path.join(os.path.expanduser("~"), "Documents", "UnrealEngine", "Python", "site-packages")):
    if os.path.isdir(_SITE) and _SITE not in sys.path:
        sys.path.append(_SITE)

from PySide6 import QtCore, QtWidgets  # noqa: E402

GENERATOR_CLASS = "BP_RoomGenerator_C"
NOTE_CLASS = "BP_Note_C"
CLUESPOT_BP = "/Game/EscapeRoom/Blueprints/BP_ClueSpot"
SPOT_FOLDER = "ER/Generator/ClueSpots"
DIFFICULTIES = ["Easy", "Medium", "Hard"]  # index = BP_RoomGenerator.Difficulty
NOTES_PER_ROOM = [1, 2, 4]                 # how many pieces the code is split into
SPOT_TAGS = ["ClueSpot", "ClueSpotMedium"]  # Medium also uses the ClueSpotMedium spots

actor_sys = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
editor_sys = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)


# ---------------------------------------------------------------- level helpers
def level_actors():
    return actor_sys.get_all_level_actors()


def actors_of(class_name):
    return [a for a in level_actors() if a.get_class().get_name() == class_name]


def is_poster(note):
    """Hard mode's symbol-order poster is a BP_Note on the PosterSpot - not a clue note."""
    parent = note.get_attach_parent_actor()
    return parent is not None and any(str(t).startswith("PosterSpot") for t in parent.tags)


def poster_note():
    posters = [n for n in actors_of(NOTE_CLASS) if is_poster(n)]
    return posters[0] if posters else None


def clue_spots(include_medium=True):
    tags = SPOT_TAGS if include_medium else SPOT_TAGS[:1]
    return [a for a in level_actors() if any(unreal.Name(t) in a.tags for t in tags)]


def is_medium_spot(spot):
    return unreal.Name("ClueSpotMedium") in spot.tags


def spot_container(spot):
    for t in spot.tags:
        if str(t) not in SPOT_TAGS:
            return str(t)
    return "?"


def medium_furniture():
    return [a for a in level_actors() if unreal.Name("Medium") in a.tags]


def show_medium_in_editor(visible):
    """Preview the layout: hide the Medium-only furniture (and its spots) in the editor viewport on Easy."""
    for a in medium_furniture() + [s for s in clue_spots() if is_medium_spot(s)]:
        a.set_is_temporarily_hidden_in_editor(not visible)


def note_text(note):
    comp = note.get_component_by_class(unreal.TextRenderComponent)
    return str(comp.get_editor_property("text")) if comp else ""


def get_generator():
    gens = actors_of(GENERATOR_CLASS)
    return gens[0] if gens else None


def generate(seed, difficulty=0):
    """Run the Blueprint generator at a difficulty (0 Easy, 1 Medium, 2 Hard).
    Returns (code, notes, spots) - 1, 2 or 4 notes, sorted by digit position - or raises."""
    gen = get_generator()
    if gen is None:
        raise RuntimeError("No RoomGenerator in this level.")
    gen.set_editor_property("Difficulty", int(difficulty))
    gen.call_method("GenerateRoom", (int(seed),))
    code = gen.get_editor_property("CurrentCode")
    notes = sorted([n for n in actors_of(NOTE_CLASS) if not is_poster(n)], key=note_text)   # "12__" sorts before "__34"
    spots = [n.get_attach_parent_actor() for n in notes]
    return code, notes, spots


def furniture_overlaps(difficulty):
    """Pairs of visible furniture whose floor footprints overlap (furniture is shuffled into slots)."""
    boxes = []
    for a in level_actors():
        if unreal.Name("Furniture") in a.tags and (difficulty >= 1 or unreal.Name("Medium") not in a.tags):
            o, e = a.get_actor_bounds(True)
            boxes.append((a.get_actor_label(), o.x - e.x, o.x + e.x, o.y - e.y, o.y + e.y))
    bad = []
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            A, B = boxes[i], boxes[j]
            if A[1] < B[2] - 2 and B[1] < A[2] - 2 and A[3] < B[4] - 2 and B[3] < A[4] - 2:
                bad.append("%s/%s" % (A[0], B[0]))
    return bad


def check_room(code, notes, spots, difficulty):
    """Is this room solvable and well laid out? Returns (ok, reason)."""
    clash = furniture_overlaps(difficulty)
    if clash:
        return False, "furniture overlaps: " + ", ".join(clash)
    want = NOTES_PER_ROOM[difficulty]
    if len(notes) != want:
        return False, "%d note(s), expected %d" % (len(notes), want)
    if any(s is None for s in spots):
        return False, "note not on a clue spot"
    if len(set(s.get_actor_label() for s in spots)) != len(spots):
        return False, "two notes on the same spot"
    if difficulty == 0 and any(is_medium_spot(s) for s in spots):
        return False, "Easy note on Medium-only furniture"
    full = "%04d" % code
    texts = [note_text(n) for n in notes]
    poster = poster_note()
    if difficulty == 2:
        # Hard: notes read "@ = 7"; the poster lists the symbols in code order, e.g. "& % # @"
        if poster is None:
            return False, "no symbol poster"
        order = note_text(poster).split()
        pairs = dict(t.split(" = ", 1) for t in texts if " = " in t)
        if len(order) != 4 or sorted(pairs) != sorted(order):
            return False, "poster %s doesn't match note symbols %s" % (order, texts)
        got = "".join(pairs[sym] for sym in order)
        return (True, "") if got == full else (False, "notes+poster give %s, code is %s" % (got, full))
    if poster is not None:
        return False, "poster should only appear on Hard"
    # each note shows its piece of the code and "_" for the digits it hides: 21__ / __13
    size = 4 // want
    expected = ["_" * (i * size) + full[i * size:(i + 1) * size] + "_" * (4 - (i + 1) * size) for i in range(want)]
    ok = texts == expected
    return (ok, "") if ok else (False, "notes %s don't match code %s" % (texts, full))


def clear_notes():
    n = 0
    for note in actors_of(NOTE_CLASS):
        actor_sys.destroy_actor(note)
        n += 1
    return n


def focus_on(actor):
    actor_sys.set_selected_level_actors([actor])
    target = actor.get_actor_location()
    cam = target + unreal.Vector(120, 120, 110)
    rot = unreal.MathLibrary.find_look_at_rotation(cam, target)
    editor_sys.set_level_viewport_camera_info(cam, rot)


def add_spot_on(actor):
    """Put a new open ClueSpot on top of the given actor's bounding box."""
    origin, extent = actor.get_actor_bounds(False)
    loc = unreal.Vector(origin.x, origin.y, origin.z + extent.z + 0.5)
    cls = unreal.EditorAssetLibrary.load_blueprint_class(CLUESPOT_BP)
    spot = actor_sys.spawn_actor_from_class(cls, loc, unreal.Rotator(0, 0, 0))
    spot.set_actor_label("Spot_" + actor.get_actor_label())
    spot.set_folder_path(SPOT_FOLDER)
    spot.tags = [unreal.Name("ClueSpot"), unreal.Name("open")]
    return spot


# ---------------------------------------------------------------- the window
class RoomTool(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Escape Room Generator")
        self.setMinimumWidth(380)
        self.last_notes = []
        self.focus_i = 0
        root = QtWidgets.QVBoxLayout(self)

        # --- Seed
        seed_box = QtWidgets.QGroupBox("Seed")
        g = QtWidgets.QGridLayout(seed_box)
        self.seed = QtWidgets.QSpinBox()
        self.seed.setRange(0, 99999)
        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.setRange(0, 99999)
        self.seed.valueChanged.connect(self.slider.setValue)
        self.slider.valueChanged.connect(self.seed.setValue)
        self.auto = QtWidgets.QCheckBox("Generate while dragging")
        self.slider.valueChanged.connect(self._slider_moved)
        b_random = QtWidgets.QPushButton("Random")
        b_gen = QtWidgets.QPushButton("Generate")
        b_clear = QtWidgets.QPushButton("Clear")
        b_focus = QtWidgets.QPushButton("Focus on clue")
        b_random.clicked.connect(self.on_random)
        b_gen.clicked.connect(self.on_generate)
        b_clear.clicked.connect(self.on_clear)
        b_focus.clicked.connect(self.on_focus)
        self.difficulty = QtWidgets.QComboBox()
        self.difficulty.addItems(DIFFICULTIES)
        self.difficulty.currentIndexChanged.connect(self.on_difficulty)
        g.addWidget(QtWidgets.QLabel("Difficulty:"), 0, 0)
        g.addWidget(self.difficulty, 0, 1)
        g.addWidget(self.seed, 1, 0)
        g.addWidget(b_random, 1, 1)
        g.addWidget(self.slider, 2, 0, 1, 2)
        g.addWidget(self.auto, 3, 0, 1, 2)
        g.addWidget(b_gen, 4, 0)
        g.addWidget(b_clear, 4, 1)
        g.addWidget(b_focus, 5, 0, 1, 2)
        self.result = QtWidgets.QLabel("-")
        self.result.setWordWrap(True)
        self.result.setStyleSheet("font-size: 14px; font-weight: bold;")
        g.addWidget(self.result, 6, 0, 1, 2)
        root.addWidget(seed_box)

        # --- Clue spots
        spot_box = QtWidgets.QGroupBox("Clue spots")
        v = QtWidgets.QVBoxLayout(spot_box)
        self.spot_list = QtWidgets.QListWidget()
        self.spot_list.itemDoubleClicked.connect(self.on_spot_clicked)
        v.addWidget(self.spot_list)
        h = QtWidgets.QHBoxLayout()
        b_add = QtWidgets.QPushButton("Add on selected actor")
        b_del = QtWidgets.QPushButton("Delete spot")
        b_ref = QtWidgets.QPushButton("Refresh")
        b_add.clicked.connect(self.on_add_spot)
        b_del.clicked.connect(self.on_delete_spot)
        b_ref.clicked.connect(self.refresh_spots)
        h.addWidget(b_add)
        h.addWidget(b_del)
        h.addWidget(b_ref)
        v.addLayout(h)
        root.addWidget(spot_box)

        # --- Batch test
        batch_box = QtWidgets.QGroupBox("Batch test")
        bv = QtWidgets.QVBoxLayout(batch_box)
        bh = QtWidgets.QHBoxLayout()
        bh.addWidget(QtWidgets.QLabel("Seeds to test:"))
        self.batch_n = QtWidgets.QSpinBox()
        self.batch_n.setRange(1, 1000)
        self.batch_n.setValue(100)
        bh.addWidget(self.batch_n)
        b_batch = QtWidgets.QPushButton("Run")
        b_batch.clicked.connect(self.on_batch)
        bh.addWidget(b_batch)
        bv.addLayout(bh)
        self.report = QtWidgets.QPlainTextEdit()
        self.report.setReadOnly(True)
        self.report.setMinimumHeight(140)
        bv.addWidget(self.report)
        root.addWidget(batch_box)

        self.refresh_spots()

    # ---- seed section
    def _slider_moved(self, _value):
        if self.auto.isChecked():
            self.on_generate()

    def on_random(self):
        self.seed.setValue(random.randint(0, 99999))
        self.on_generate()

    def on_difficulty(self, index):
        show_medium_in_editor(index >= 1)
        self.refresh_spots()
        self.on_generate()

    def on_generate(self):
        seed, diff = self.seed.value(), self.difficulty.currentIndex()
        try:
            code, notes, spots = generate(seed, diff)
        except Exception as e:
            self.result.setText("Error: %s" % e)
            return
        self.last_notes, self.focus_i = notes, 0
        parts = ["%s @ %s" % (note_text(n), s.get_actor_label() if s else "?") for n, s in zip(notes, spots)]
        if poster_note():
            p = poster_note()
            where = "behind the painting" if "Hidden" in p.get_attach_parent_actor().get_actor_label() else "on the painting"
            parts.append("poster: %s  (%s)" % (note_text(p), where))
        ok, why = check_room(code, notes, spots, diff)
        self.result.setText("Seed %d [%s]  ->  Code %04d\n%s%s" % (
            seed, DIFFICULTIES[diff], code, "\n".join(parts), "" if ok else "\nPROBLEM: " + why))

    def on_clear(self):
        n = clear_notes()
        self.last_notes = []
        self.result.setText("Cleared %d note(s)" % n)

    def on_focus(self):
        notes = actors_of(NOTE_CLASS)
        if notes:
            notes = sorted(notes, key=note_text)
            focus_on(notes[self.focus_i % len(notes)])   # press again to jump to the next note
            self.focus_i += 1
        else:
            self.result.setText("No clue in the level - press Generate first")

    # ---- clue spot section
    def refresh_spots(self):
        self.spot_list.clear()
        medium = self.difficulty.currentIndex() >= 1
        for s in sorted(clue_spots(include_medium=medium), key=lambda a: a.get_actor_label()):
            extra = "  (Medium)" if is_medium_spot(s) else ""
            item = QtWidgets.QListWidgetItem("%s   [%s]%s" % (s.get_actor_label(), spot_container(s), extra))
            item.setData(QtCore.Qt.UserRole, s.get_actor_label())
            self.spot_list.addItem(item)

    def _spot_by_label(self, label):
        for s in clue_spots():
            if s.get_actor_label() == label:
                return s
        return None

    def on_spot_clicked(self, item):
        s = self._spot_by_label(item.data(QtCore.Qt.UserRole))
        if s:
            focus_on(s)

    def on_add_spot(self):
        sel = actor_sys.get_selected_level_actors()
        if not sel:
            self.result.setText("Select a piece of furniture in the level first")
            return
        with unreal.ScopedEditorTransaction("Add ClueSpot"):
            for a in sel:
                add_spot_on(a)
        self.refresh_spots()

    def on_delete_spot(self):
        item = self.spot_list.currentItem()
        if not item:
            return
        s = self._spot_by_label(item.data(QtCore.Qt.UserRole))
        if s:
            with unreal.ScopedEditorTransaction("Delete ClueSpot"):
                actor_sys.destroy_actor(s)
        self.refresh_spots()

    # ---- batch section
    def on_batch(self):
        n = self.batch_n.value()
        diff = self.difficulty.currentIndex()
        counts, passed, failures = {}, 0, []
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        try:
            for seed in range(n):
                code, notes, spots = generate(seed, diff)
                ok, why = check_room(code, notes, spots, diff)
                if ok:
                    passed += 1
                    for spot in spots:
                        label = spot.get_actor_label()
                        counts[label] = counts.get(label, 0) + 1
                else:
                    failures.append("%d (%s)" % (seed, why))
        except Exception as e:
            self.report.setPlainText("Batch stopped: %s" % e)
            return
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()
            clear_notes()
        per_room = NOTES_PER_ROOM[diff]
        lines = ["[%s] %d / %d rooms passed (no furniture overlap, %d note(s) on allowed spots, code adds up)"
                 % (DIFFICULTIES[diff], passed, n, per_room), ""]
        lines.append("Where the clues landed:")
        for label, c in sorted(counts.items(), key=lambda kv: -kv[1]):
            lines.append("  %-22s %4d  %s" % (label, c, "#" * max(1, c * 30 // (n * per_room))))
        if failures:
            lines += ["", "Failed seeds: %s" % failures[:20]]
        self.report.setPlainText("\n".join(lines))
        unreal.log("[er_tool] batch %s: %d/%d passed" % (DIFFICULTIES[diff], passed, n))


# ---------------------------------------------------------------- Qt inside Unreal
_app = None
_window = None
_tick = None


def _pump(_dt):
    if _app is not None:
        _app.processEvents()


def show():
    """Open (or bring back) the tool window."""
    global _app, _window, _tick
    _app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    if _tick is None:
        _tick = unreal.register_slate_post_tick_callback(_pump)
    if _window is None or not isinstance(_window, RoomTool):
        _window = RoomTool()
        _window.setWindowFlags(_window.windowFlags() | QtCore.Qt.Tool)
    _window.show()
    _window.raise_()
    try:
        unreal.parent_external_window_to_slate(int(_window.winId()))
    except Exception:
        pass
    _window.refresh_spots()
    return _window


# ---------------------------------------------------------------- menu bar entry
def register_menu():
    menus = unreal.ToolMenus.get()
    main = menus.find_menu("LevelEditor.MainMenu")
    if main is None:
        return
    sub = main.add_sub_menu("EscapeRoom", "EscapeRoomSection", "EscapeRoom", "Escape Room")
    entry = unreal.ToolMenuEntry(name="ERRoomTool", type=unreal.MultiBlockType.MENU_ENTRY)
    entry.set_label("Room Generator Tool")
    entry.set_tool_tip("Open the Escape Room generator tool window")
    entry.set_string_command(unreal.ToolMenuStringCommandType.PYTHON, "",
                             "import er_tool; er_tool.show()")
    sub.add_menu_entry("Tools", entry)
    menus.refresh_all_widgets()
