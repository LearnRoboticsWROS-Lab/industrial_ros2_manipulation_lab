# Vision-Guided Pick and Place

**A camera finds a red object by colour, and the robot picks it up wherever it
lands.** A hard-coded pick-and-place fails the moment the object moves; add a
camera and the robot finds the target at runtime.

This is a **YouTube demo project** on the Industrial ROS2 Manipulation Lab. It
runs entirely in simulation, on the free Starter cell, in two commands.

```bash
./scripts/lab build                          # once
./scripts/lab youtube run vision_pick_place  # start the cell + the demo
```

## What this project does

```
RGB-D camera ─► detect red object (colour) ─► pixel + depth ─► 3D point
           ─► TF2 (camera → base_link) ─► fixed top-grasp ─► MoveIt2 motion
           ─► pick ─► lift ─► place
```

It **reuses the cell** and does not reimplement any of it: the UR5 + Robotiq +
depth-camera description, the MoveIt2 configuration, the `ros2_control`
controllers, and the Gazebo `LinkAttacher` grasp all come from the Lab.

The demo adds exactly three small nodes:

| Node | Language | Job |
|---|---|---|
| `perception_node.py` | Python + OpenCV | find the red object, publish a 3D target pose |
| `spawn_target.py` | Python | drop the object at a random valid spot; `/yt_vision/randomize` to repeat |
| `pick_place_node` | C++ + MoveIt2 | plan → grasp → attach → lift → place |

## Prerequisites

The Starter edition, built once (`./scripts/lab build`). No hardware, no
RealSense, no Jetson. Ubuntu 22.04 or Windows 11 + WSL2, per the Lab setup docs.

## Run

```bash
./scripts/lab youtube run vision_pick_place
```

Gazebo and RViz open, the object appears at a random position, the camera finds
it, and the robot picks and places it.

### The collision-scene toggle (why "just let the planner do it" isn't enough)

By default the demo tells MoveIt about the tables, so OMPL plans around them.
Turn that off and watch what happens:

```bash
./scripts/lab youtube run vision_pick_place use_collision_scene:=false
```

With no obstacles in the scene, the planner has no idea the tables exist: it
finds a *different* path every run, swings the arm through the table, and
sometimes fails outright. That is not a bug — it is the point. Free-space
planning to a pose, with no strategy, is unpredictable. Making a pick-and-place
**predictable, safe and repeatable** — a controlled straight-line approach,
planner choice, retreat, and recovery when a plan fails — is engineering, and
that is the Simulation Track.

### Choosing a motion planner: OMPL vs Pilz

```bash
./scripts/lab youtube run vision_pick_place motion_planning:=ompl   # default
./scripts/lab youtube run vision_pick_place motion_planning:=pilz   # industrial PTP
```

- **OMPL** (default) samples the free space and routes *around* obstacles — safe,
  but the path is different every run and doesn't look industrial.
- **Pilz** does deterministic, repeatable point-to-point (PTP) motion, the way a
  real industrial controller moves — but it goes the *direct* way: it
  collision-checks and *fails* rather than detouring. With the tables in the
  scene, a blocked segment simply won't plan.

That trade-off is the lesson: a working demo doesn't tell you *which* planner an
application needs. Hitting a fixed, safe cycle time — PTP for travel, a straight
LIN approach, avoiding singularities, knowing when to use each — is the
engineering the Simulation Track teaches. This demo uses a single planner for
everything, on purpose.

### Do it again with the object somewhere else

In a second terminal:

```bash
./scripts/lab exec ros2 service call /yt_vision/randomize std_srvs/srv/Trigger {}
./scripts/lab exec ros2 service call /yt_vision/run       std_srvs/srv/Trigger {}
```

The object moves, the camera re-detects it, the robot picks it again — proving
the coordinates are not hard-coded.

## Expected result

1. The red object is spawned at a random `(x, y)` on the work surface.
2. `perception_node` logs `target @ base (x, y, z)` and publishes a marker you
   can see in RViz.
3. The arm moves to a pre-grasp pose above the object, descends, closes the
   gripper, and the object attaches.
4. The arm lifts, moves to the place location, releases, and returns home.

## Main ROS interfaces

| Interface | Type | Direction |
|---|---|---|
| `/camera/image_raw`, `/camera/depth/image_raw`, `/camera/camera_info` | sensor_msgs | in (from the cell) |
| `/yt_vision/target_pose` | geometry_msgs/PoseStamped | perception → motion |
| `/yt_vision/target_marker` | visualization_msgs/Marker | to RViz |
| `/yt_vision/run` | std_srvs/Trigger | run one pick-and-place |
| `/yt_vision/randomize` | std_srvs/Trigger | move the object to a new spot |
| `/ATTACHLINK`, `/DETACHLINK` | linkattacher_msgs | the simulated grasp |

Everything is tunable in [config/params.yaml](config/params.yaml) — topics,
HSV thresholds, the pick region, grasp heights, the place location, gripper
open/close, motion speed. You should not need to edit code to adapt the demo.

## Known limitations — and why they are fine

This project is a **vertical slice**: it solves one task, well, and stops there.

- one object, one colour (a plain HSV colour threshold, not a real detector)
- a fixed top-down grasp orientation
- sequential control flow, no state machine
- simulation only
- planning is left to OMPL with no strategy: no controlled straight-line (LIN)
  approach, no planner choice — the path differs every run (try
  `use_collision_scene:=false` to see it with no obstacles at all)
- **no automated recovery**: if detection or planning fails, it stops and tells
  you — it does not retry, re-plan, or fall back

These are the **scope**, not defects. The code is clean, parameterised and
readable on purpose. What it deliberately leaves out is the *engineering*.

## What this deliberately does NOT do

The moment you ask any of these questions, you have left the demo and entered
system engineering:

> What if detection fails? What if planning fails? How do we retry and recover?
> How do we reuse "pick" in another task? How do we swap the detector or the
> gripper without a rewrite? How do we orchestrate several skills? How do we
> configure a different process without touching code?

Turning this slice into **reusable perception and manipulation skills, a
Behavior Tree architecture, failure handling and recovery, and a configurable,
robot-agnostic system** is exactly what the **Simulation Track** teaches — and
the **Full Track** then deploys the same architecture on a real robot.

→ <https://www.learn-robotics-with-ros.com>

## Exercises

Stay well inside the free scope and still learn a lot:

1. **Change the target.** Point the HSV thresholds in `params.yaml` at a
   different colour (edit the object's material, or spawn a different one).
2. **Change the reachable area.** Widen `x_min/x_max/y_min/y_max` and see where
   detection or planning starts to struggle.
3. **Change the grasp.** Adjust `grasp_z_offset` and the grasp RPY; watch how
   the approach changes.
4. **Visualise the target.** Add the `/yt_vision/target_marker` marker in RViz
   and confirm it lands on the object.
5. **Change the place location.** Move `place_x/place_y/place_z` and re-run.

A natural next question — *"refactor this into reusable skills and a Behavior
Tree"* — is intentionally **not** a free exercise. That is the Simulation Track.
