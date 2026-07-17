# Practice Guide — make the cell yours

Launching the workcell is not learning. **Changing it and predicting what happens
is.** This guide turns the Starter Edition into a place to practise, and gives
you a sandbox where you cannot break anything that matters.

Do these in order. Each one takes 15–30 minutes and teaches one habit you will
use for the rest of your robotics career.

---

## First: build yourself a sandbox

The single most useful habit: **never make your first change to a file you cannot
restore.**

```bash
# from the repo root
mkdir -p sandbox
cp -r src/lrwros_ur5_workcell sandbox/my_workcell_experiments
```

Rules that will save you hours:

1. **Work in `sandbox/`.** Nothing there is part of the lab. Break it freely.
2. **Change one thing at a time**, then relaunch. Two changes means two suspects.
3. **`git diff` before you ask for help.** Nine times out of ten you will find it yourself.
4. **When lost:** `git checkout -- .` puts the core back exactly as it shipped.

> `sandbox/` is yours. Nothing in the lab reads it, so nothing in the lab can be
> broken by it.

## Files to look at

| File | What it tells you |
|---|---|
| `src/lrwros_ur5_workcell/urdf/` | the robot description — links, joints, the gripper, the camera |
| `src/lrwros_ur5_workcell/worlds/` | the world: the table, the object, the pallet |
| `src/lrwros_ur5_workcell/config/` | controller configuration |
| `src/lrwros_bringup/launch/module_03.launch.py` | how the whole cell is started |

## Files to leave alone at first

| File | Why |
|---|---|
| `docker/` | changing the image means 30-minute rebuilds to find a typo |
| `scripts/lab` and friends | the entry point; break it and every command breaks |
| `.repos/simulation_dependencies.repos` | this is what fetches the UR5 and Robotiq sources. Delete a line and nothing builds |

Come back to these once the cell holds no mystery.

---

## Exercise 1 — Move the object

**Goal:** change the world and predict the result before you look.

1. Find the object in `src/lrwros_ur5_workcell/worlds/`.
2. Find its `<pose>`: six numbers, `x y z roll pitch yaw`, in **metres and radians**.
3. Move it 10 cm along X: change the first number by `0.1`.
4. **Before relaunching, say out loud which way it will move.** Then:
   `./scripts/lab start module_03`

**What you learn:** poses are `x y z r p y`, units are SI, and Gazebo believes
your file exactly. Get the sign wrong and the object is behind the robot — which
is a lesson, not a mistake.

## Exercise 2 — Read the robot description

**Goal:** stop seeing the URDF as XML soup.

1. Open `src/lrwros_ur5_workcell/urdf/`. Find where the UR5, the gripper and the camera are brought together.
2. Inside the container, expand the description into what ROS actually receives:
   ```bash
   ./scripts/lab exec bash
   ros2 topic echo /robot_description --once | head -40
   ```
3. In RViz, add the **TF** display. Find `base_link`, `tool0`, the camera frame.
4. Answer, from the file: **which link is the camera attached to, and how far from it?**

**What you learn:** the URDF is a tree, and TF is that tree, live. Every frame in
RViz is a claim your description made.

## Exercise 3 — Drive the arm from MoveIt

**Goal:** feel the difference between a plan and an execution.

1. Launch the cell. In RViz, open **MotionPlanning**.
2. Drag the marker somewhere reachable → **Plan** → watch the ghost → **Execute**.
3. Now drag it somewhere **impossible** — inside the table, or far out of reach.
4. Click **Plan**. Read the terminal: MoveIt tells you *why* it failed.
5. Try a pose that is reachable but only through a tight gap. Plan several times —
   **notice the path is different each run.**

**What you learn:** planning is a search, not a formula. It can fail, it can take
time, and it is randomised. Every robotics engineer learns this eventually; you
just did it in ten minutes.

## Exercise 4 — Change a configuration value

**Goal:** touch the control layer without breaking it.

1. Look in `src/lrwros_ur5_workcell/config/` for the controller YAML.
2. Find a velocity or acceleration scaling value.
3. Halve it. Rebuild and relaunch:
   ```bash
   ./scripts/lab build && ./scripts/lab start module_03
   ```
4. Plan and execute the same motion. **It should be visibly slower.**
5. Now put it back — `git checkout -- .` — and confirm it is fast again.

**What you learn:** behaviour lives in configuration, not code. This is the whole
idea behind the architecture the paid track teaches: the *what* is data, the
*how* is code, and you change the data.

## Exercise 5 — Write it down

**Goal:** the habit that separates an engineer from someone who once got it working.

Create `sandbox/EXPERIMENTS.md` and, for each exercise above, record:

```markdown
## Experiment: moved the object 10cm in X
- What I changed:  worlds/..., object pose x: 0.5 -> 0.6
- What I expected: the object moves away from the robot
- What happened:   it moved toward the robot
- Why:             X points back toward the base; I had the axis backwards
- Command to redo: ./scripts/lab start module_03
```

**What you learn:** the "why" line is the one that matters, and it is the one
everybody skips. Six months from now this file is worth more than the code.

---

## When you have done all five

You can now: launch an industrial cell, read its description, move its robot,
change its world, tune its controllers, and restore it when you break it.

**What you cannot do yet** is make it *do a task on its own* — decide what to
pick, find it with a camera, sequence the grasp, recover when it fails. Nothing
in this edition does that, because that is the course:

- **Simulation Track** — blind pick-and-place → vision-guided pick-and-place →
  a Behavior Tree architecture → your capstone
- **Full Track** — all of that, then deployed on a **real** industrial cobot with
  a RealSense and a Jetson

**[UPGRADE.md](UPGRADE.md)**

You are ready for it when the exercises above feel obvious — not before. The cell
holding no mystery is exactly the right place to start building on top of it.
