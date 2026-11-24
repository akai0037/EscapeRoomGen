# Escape Room White-Box Generator

Research Project 1 — an Unreal Engine 5.8 tool that builds a new, solvable **white-box (grey-box) escape room** from a seed: room size, furniture layout, puzzle type, where the clues are hidden and the code that opens the door all change every time, and a batch test checks that the rooms are solvable (every difficulty × puzzle combination passes 100 / 100 seeds).

- **Engine:** Unreal Engine 5.8 (First Person template)
- **Game logic:** Blueprints (`BP_RoomGenerator.GenerateRoom`)
- **Editor tool:** Python + PySide6 panel (`Content/Python/er_tool.py`, `er_layout.py`)
- **Video (1–3 min):** [EscapeRoomGen.mp4 on Google Drive](https://drive.google.com/file/d/1i756jnqWHiE4OS5oX5MOyAYOiv6fvPzx/view?usp=sharing)

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
- **Puzzle type became its own choice.** At first I went deeper on the number lock only (Easy, Medium and Hard split the code into 1, 2 or 4 notes, and Hard had a symbol-order poster). In the last week I made the puzzle type a separate option next to difficulty: **Number**, **Symbol**, **Color** and **Key**. Every type ends in the same number-lock door, so one solvability check covers all of them.
- **Color is a colour-order puzzle, not lights.** Instead of lights you switch on in order, the colour puzzle uses notes that show only digits printed in a colour (e.g. `21` in red) plus a poster with the colour order. It reuses the symbol system, so I could test it the same way.
- **The key puzzle avoids the dead end by design.** One note goes into a lock box and the key is placed exactly where that note would have been, so the key can never end up inside the box. There is no inventory: picking up the key unlocks the box directly.
- **The room itself is generated too.** This wasn't in my proposal: room size and furniture layout change with difficulty, so rooms look different, not only the clues.
- **I added an editor tool.** Generating only at play time made it hard to see where clues went or to test many rooms, so I built a Python/PySide panel in Unreal, like the tools I made for Maya.
- **It became a white-box generator.** I tried two Fab furniture packs, but together they were about 3.4 GB, much more than GitHub LFS's 1 GB free limit. I kept grey-box furniture and wrote a guide for swapping in real models later.

**Not done from the proposal:** a light-switching puzzle, chaining several different puzzles in one room, a timer, sound, and lighting polish (see *What doesn't work yet* and *Next steps*).

**A note on the commit history:** I started building the project in Unreal around Nov 9 but only put it in a Git repository on Nov 22, so the commits only cover the last two days.

## What I made

**In the game**
- Start screen: pick **Easy / Medium / Hard** and a seed (or a random one), then *Generate & Start*.
- First-person movement, **E** to interact (drawers slide open, the painting slides aside, the door opens with the right code on a keypad).
- After escaping: **Play Again** or **Quit**.

**What the generator does (`GenerateRoom`, one seed → one room)**
1. Clears the last room and seeds a random stream, then rolls a 4-digit code.
2. **Room size per difficulty** — moves the walls, floor, ceiling and door to that difficulty's layout (current settings: Easy 8 × 6 m, Medium 10 × 7 m, Hard 12 × 12 m; editable in the panel).
3. **Furniture shuffle** — places that difficulty's furniture (3 / 5 / 12 pieces — Hard asks for 16, but a 12 × 12 m room only has 12 slots) into random free slots along the walls, so no two rooms look the same and pieces never overlap. **Paintings count as furniture:** each hangs on the wall above its own slot, every room has the painting that can hide the order poster (Symbol / Color puzzles), and bigger rooms add up to two more paintings (they slide aside too, but hide nothing — decoys).
4. **Clues** — picks clue spots only on furniture that is actually in the room. Difficulty sets how many notes the code is split into (Easy 1, Medium 2, Hard 4); the **puzzle type** (`PuzzleType`, chosen in the editor panel) sets what they look like:

   | Puzzle | Notes | Extra | Difficulties |
   |---|---|---|---|
   | **Number** | `21__`, `__13` (Hard: `2___` … `___3`) | — | all |
   | **Symbol** | `@ = 21` | **symbol-order poster** (e.g. `& # % @`, one of 24 orders), on the painting or **hidden behind it** — slide the painting aside with E | Medium, Hard |
   | **Color** | just the digits, printed in a colour (e.g. `21` in red) | colour-order poster (e.g. `GREEN RED BLUE ORANGE`) | Medium, Hard |
   | **Key** | number notes, but one is in a **lock box** in the middle of the room | the **key** lies where that note would have been; pick it up with E, then open the box with E | all |

   Symbol and Color need at least two notes to put in order, so they are not offered on Easy.
   The text comes from small Blueprint functions on the generator: `ClueText`, `ClueColor`, `Decorate` (symbols → colour words) and `UsesPoster`; the key puzzle is `ApplyKeyPuzzle`.

**Editor panel (Escape Room → Room Generator Tool)**
- Generate any seed / difficulty / puzzle type in the editor and see where every clue (and the key) went; *Focus on clue* jumps the camera to it. The puzzle type you pick is also what the game uses when you press Play.
- **Room layout:** width, depth and furniture count for each difficulty. *Apply layout* recomputes walls, door and furniture slots (one slot per 3 m of wall) and copies extra furniture when a room needs more. The furniture count includes the paintings and can't exceed the number of slots — if you ask for more, the panel says how many fit and that the room needs to be bigger.
- **Clue spots:** list, add (on the selected actor) and delete the places notes can appear.
- **Batch test:** generates N seeds and checks every room — no furniture overlap or furniture outside the walls, the right number of notes, notes only on furniture that is in the room, and the notes (+ poster) really add up to the door code. For Color it also checks each note is plain digits in one of the four colours; for Key it checks exactly one note is in the box and the key is on a normal clue spot in the room (never inside the box). Every difficulty × puzzle combination passes 100 / 100.

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
- **Recompiling Blueprints** (not only `BP_Drawer`) can snap the drawer clue spots to the front of the drawer instead of its floor, so notes stick out of the drawer front. *Apply layout* in the panel fixes it — press it after compiling any Blueprint.
- The **puzzle type** can only be chosen in the editor panel; the in-game start screen only picks difficulty and seed.
- The **lock box** always stands in the middle of the room, and the note that goes into it is not picked very evenly (on most seeds it is the same note).
- Running the generator in the editor leaves the last room's furniture positions and difficulty in the level (the game always regenerates on start, so it does not affect play).
- The player always starts at the same spot near the door; it is not moved for bigger rooms.
- No timer, sound or hint system yet.

## Next steps

- Chain different puzzle types in one room (e.g. the colour poster is locked in the key box), and a light-switching puzzle from my proposal.
- Move the lock box to a random free spot instead of the middle of the room.
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
1. **Apply layout** (re-attaches drawer spots to the sliding drawer — always do this after compiling a Blueprint).
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
| `Content/EscapeRoom/Blueprints/BP_LockBox`, `BP_Key` | Key puzzle: the box opens with E only after the key was picked up |
| `Content/EscapeRoom/UI/WBP_StartPanel`, `WBP_Keypad`, `WBP_Win` | Start screen, door keypad, win screen |
| `Content/Python/er_tool.py` | Editor panel (generate, clue spots, room layout, batch test) |
| `Content/Python/er_layout.py`, `room_layout.json` | Room size / furniture count per difficulty |
| `Scripts/` | Helper scripts used while building the level |
