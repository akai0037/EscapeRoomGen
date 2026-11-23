# Escape Room White-Box Generator

Research Project 1 — an Unreal Engine 5.8 tool that builds a new, solvable **white-box (grey-box) escape room** from a seed: room size, furniture layout, where the clues are hidden and the code that opens the door all change every time, and every room is guaranteed to be solvable.

- **Engine:** Unreal Engine 5.8 (First Person template)
- **Game logic:** Blueprints (`BP_RoomGenerator.GenerateRoom`)
- **Editor tool:** Python + PySide6 panel (`Content/Python/er_tool.py`, `er_layout.py`)
- **Video (1–3 min):** _add link here_

---

## Goal

Level designers spend a lot of time hand-placing escape-room props and checking that the puzzle can still be solved. I wanted a generator that does the boring part — lay out a room, hide the clues, make sure the code adds up — so a designer can press a button, get a playable white-box room, test it, and only then spend time on art. The rooms stay deliberately simple (grey boxes) so the layout and puzzle flow are easy to read, and any piece can be swapped for a real model later (see [Swapping in your own models](#swapping-in-your-own-models)).

## How it changed from the proposal

**What I proposed:** a Blueprint system in UE5 that builds a new, solvable escape room every time you play, with 2–3 puzzle types (number lock, light/color order, hidden key) chained so one puzzle unlocks the next, plus a start screen, timer, sound and lighting polish.

**What stayed the same**
- Every play is a new room, and the answer (the door code) and clue positions are randomized each time.
- The riskiest part of my proposal was making sure every room is actually solvable. That part is done: the batch test generates hundreds of seeds and checks that the clues really add up to the door code, every note is on furniture that is in the room, and nothing overlaps.
- Start screen, number-lock door and win screen work.

**What changed, and why**
- **One puzzle that scales, instead of three puzzle types.** I went deeper on the number lock instead of building light/color order and hidden key. Easy, Medium and Hard split the code into 1, 2 or 4 notes, and Hard adds a symbol-order poster that is sometimes hidden behind a sliding painting. Each new puzzle type needs its own interaction and its own solvability check, and I wanted every room to be checked, not just look random.
- **No hidden key.** I considered a key-and-lock box for Hard but chose the poster. A key needs picking up and an inventory, and it is exactly the dead-end risk I wrote about (a key locked inside the box it opens).
- **The room itself is generated too.** This wasn't in my proposal: room size and furniture layout change with difficulty, so rooms look different, not only the clues.
- **I added an editor tool.** Generating only at play time made it hard to see where clues went or to test many rooms, so I built a Python/PySide panel in Unreal, like the tools I made for Maya.
- **It became a white-box generator.** I tried two Fab furniture packs, but together they were about 3.4 GB, much more than GitHub LFS's 1 GB free limit. I kept grey-box furniture and wrote a guide for swapping in real models later.

**Not done from the proposal:** the light/color order and hidden-key puzzles, chaining puzzles so one unlocks the next, a timer, sound, and lighting polish (see *What doesn't work yet* and *Next steps*).

## What I made

**In the game**
- Start screen: pick **Easy / Medium / Hard** and a seed (or a random one), then *Generate & Start*.
- First-person movement, **E** to interact (drawers slide open, the painting slides aside, the door opens with the right code on a keypad).
- After escaping: **Play Again** or **Quit**.

**What the generator does (`GenerateRoom`, one seed → one room)**
1. Clears the last room and seeds a random stream, then rolls a 4-digit code.
2. **Room size per difficulty** — moves the walls, floor, ceiling and door to that difficulty's layout (defaults: Easy 8 × 6 m, Medium 10 × 7 m, Hard 12 × 8 m).
3. **Furniture shuffle** — places that difficulty's furniture (3 / 5 / 7 pieces) into random free slots along the walls, so no two rooms look the same and pieces never overlap. **Paintings count as furniture:** each hangs on the wall above its own slot, every room has the painting that can hide the Hard poster, and bigger rooms add up to two more paintings (they slide aside too, but hide nothing — decoys on Hard).
4. **Clues** — picks clue spots only on furniture that is actually in the room:
   - **Easy:** one note with the whole code.
   - **Medium:** two notes, first half / second half (`21__`, `__13`).
   - **Hard:** four notes that read `symbol = digit` (e.g. `@ = 7`) plus a **symbol-order poster** (e.g. `& # % @`, one of 24 orders). By seed, the poster is either on the painting or **hidden behind it** — slide the painting aside with E to find it.

**Editor panel (Escape Room → Room Generator Tool)**
- Generate any seed / difficulty in the editor and see where every clue went; *Focus on clue* jumps the camera to it.
- **Room layout:** width, depth and furniture count for each difficulty. *Apply layout* recomputes walls, door and furniture slots (one slot per 3 m of wall) and copies extra furniture when a room needs more. The furniture count includes the paintings and can't exceed the number of slots — if you ask for more, the panel says how many fit and that the room needs to be bigger.
- **Clue spots:** list, add (on the selected actor) and delete the places notes can appear.
- **Batch test:** generates N seeds and checks every room — no furniture overlap or furniture outside the walls, the right number of notes, notes only on furniture that is in the room, and the notes (+ poster on Hard) really add up to the door code. All three difficulties pass 100 / 100.

## How to run

1. Install [Git LFS](https://git-lfs.com/), then clone this repo (`git clone` pulls the `.uasset` / `.umap` files through LFS).
2. Open `EscapeRoomGen.uproject` with Unreal Engine 5.8. The level `Content/EscapeRoom/Maps/Lvl_EscapeRoom` opens.
3. Press **Play**. Choose a difficulty with the *Difficulty* button, optionally type a seed, then *Generate & Start*.
   - **WASD** move, mouse look, **E** interact, **Shift + F1** frees the mouse in the editor.
4. Editor tool: menu **Escape Room → Room Generator Tool**. The panel needs PySide6 in `Content/Python/site-packages` or `Documents/UnrealEngine/Python/site-packages`.

> ⚠️ Close the Room Generator panel before compiling any Blueprint — compiling while it is open crashes the editor (see *What doesn't work yet*).

## What I learned

- **A seed makes randomness testable.** At first I thought "random" just meant different every time. But if every choice comes from one `RandomStream`, the same seed always builds the same room. That changed how I debugged: when something looked wrong, I wrote down the seed and could rebuild that exact room again. It's also what made the batch test possible.

- **I can't just assume the room is solvable. I have to check it.** I thought my logic was right, but the batch test and play-testing kept finding problems I didn't expect: a note stuck inside the drawer's front panel, notes showing up on furniture that wasn't even in the Easy room, and drawer clue spots that stopped moving with the drawer after I recompiled the Blueprint. Now I think the checking tool is as important as the generator itself.

- **Tags are a simple way to control a lot of things.** Instead of making a separate Blueprint for each difficulty, I tagged actors (`Furniture<d>`, `FurnitureSlot<d>`, `ClueSpot<d>`). One `GenerateRoom` graph can then handle every difficulty and room size, and the editor panel can change the room without me opening the Blueprint.

- **Do the heavy work in the editor, keep the game logic small.** The Python panel calculates the room layouts ahead of time and saves them as arrays on the generator. In the game, the Blueprint only applies them. This kept my Blueprint graph much shorter and easier to follow.

- **Scope is a design decision too.** I wanted real furniture models, so I tried two Fab packs. Together they were about 3.4 GB, much more than GitHub LFS's 1 GB free limit. So I kept the room white-box and wrote a guide for swapping models in later. The generator is the real point of the project, and grey boxes actually make the layout and puzzle flow easier to see.

- **Tools can break each other.** Compiling a Blueprint while my PySide panel was open crashed Unreal. I didn't fix it yet, but I learned that Python and Qt hold references to editor objects, and those can break when a Blueprint recompiles. For now I close the panel first.

- **Keeping a big Blueprint readable.** As `GenerateRoom` grew, it got hard to follow. I deleted unused nodes and grouped the graph into commented sections in the same order the room gets built, so I (and anyone else) can read it from left to right.

## What doesn't work yet

- **Editor crash:** compiling a Blueprint while the Python/Qt Room Generator panel is open crashes Unreal (access violation in Python). Workaround: close the panel first.
- **Lighting:** there is one ceiling light; big Hard rooms are a bit dim at the corners, and the desk-lamp light does not move with the desk.
- **Recompiling `BP_Drawer`** re-attaches the drawer clue spots to the cabinet instead of the sliding drawer. *Apply layout* in the panel fixes it — press it after editing `BP_Drawer`.
- Running the generator in the editor leaves the last room's furniture positions and difficulty in the level (the game always regenerates on start, so it does not affect play).
- The player always starts at the same spot near the door; it is not moved for bigger rooms.
- No timer, sound or hint system yet.

## Next steps

- The puzzle types from my proposal: a **light/color order** puzzle and a **hidden key** for a locked chest, chained so one puzzle unlocks the next (and checked by the batch test so the key is never locked inside its own chest).
- A **clock** whose hands show part of the code.
- Room shapes beyond rectangles (L-shaped rooms, two connected rooms).
- Lights that scale with room size; desk lamp attached to the desk.
- Timer, sound effects and a hint button.
- Fix the panel/compile crash (release Python references before Blueprints recompile).
- Optional art pass: swap the white-box furniture for real models (guide below).

---

## Swapping in your own models

The generator only cares about each furniture Blueprint's **name and tags**, the sliding part called **`Drawer`** in `BP_Drawer`, and the **clue spot** actors attached to the furniture. The look can be anything.

### 1. The white-box rules
- The furniture Blueprints are in `Content/EscapeRoom/Blueprints/`: `BP_Shelf` (bookshelf), `BP_DeskSet` (desk + chair), `BP_Drawer` (drawer cabinet).
- The **front faces +X** (the red arrow in the viewport). The origin is on the floor, and the **back sits at about X = −25**, against the wall.
- Keep new models within about **2.5 m wide (Y)** and **0.6 m deep (X)**, otherwise they may overlap other furniture — the batch test will tell you.

### 2. Add the new model
1. Open the Blueprint (e.g. `BP_Shelf`).
2. **Components → + Add → Static Mesh**, then pick your model in **Details → Static Mesh**.
3. Move / rotate / scale it so its back touches X = −25, its bottom touches the floor and its front faces +X. Many Fab models face Y — set **Rotation Z** to −90 or 90.

### 3. Hide the cubes (don't delete them)
Select each cube part (`Board0`, `SideL`, `Cabinet`, …) and in Details:
- **Rendering → Visible**: off
- **Collision → Collision Presets**: `NoCollision`

To go back to the white box, switch those two settings back.

### 4. Drawers (`BP_Drawer`)
- Drag the drawer model **under the `Drawer` component** so it slides out when the player presses E.
- Keep `Drawer`'s own collision on — the E interaction traces against it.
- `Drawer` is scaled, so set the child's **Scale to Absolute** (the lock icon next to Scale) or the model will be squashed.
- The slide distance is **Class Defaults → Open Distance**; make it smaller for shallow drawers.

### 5. Compile and save
**Close the Room Generator panel first**, then **Compile** and **Save**.

### 6. Move the clue spots
- In the level, the `Spot_…` actors attached to the piece (expand it in the Outliner) are where notes appear. Drag them onto the new model's surfaces, about 0.5 cm above the top.
- To add another spot: select the furniture, then **Clue spots → Add on selected actor** in the panel.
- Don't forget the copies made for bigger rooms (e.g. `BP_Shelf_6`).

### 7. Apply and test
In **Escape Room → Room Generator Tool**:
1. **Apply layout** (re-attaches drawer spots to the sliding drawer — always do this after editing `BP_Drawer`).
2. Run **Batch test** for each difficulty and check it says 100 / 100.
3. Press Play and walk around.

### 8. Before committing
Fab / Marketplace packs are huge (the two packs I tried were ~3.4 GB together; GitHub LFS's free tier is 1 GB). Move only the models you use — with their materials and textures — into `Content/EscapeRoom/Fab/` and reduce textures to 1K before committing. `Content/Cigar_room/`, `Content/UnrealBucket/` and `Content/Fab/` are already in `.gitignore`.

---

## Project layout

| Path | What it is |
|---|---|
| `Content/EscapeRoom/Maps/Lvl_EscapeRoom` | The room level |
| `Content/EscapeRoom/Blueprints/BP_RoomGenerator` | The generator (`GenerateRoom`) |
| `Content/EscapeRoom/Blueprints/BP_Shelf`, `BP_DeskSet`, `BP_Drawer`, `BP_Painting`, `BP_Door`, `BP_Note`, `BP_ClueSpot`, `BP_FurnitureSlot` | Furniture, interactables and helpers |
| `Content/EscapeRoom/UI/WBP_StartPanel`, `WBP_Keypad`, `WBP_Win` | Start screen, door keypad, win screen |
| `Content/Python/er_tool.py` | Editor panel (generate, clue spots, room layout, batch test) |
| `Content/Python/er_layout.py`, `room_layout.json` | Room size / furniture count per difficulty |
| `Scripts/` | Helper scripts used while building the level |
