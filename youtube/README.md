# YouTube Projects

Small, self-contained robotics demos you can run on the Lab in two commands.
Each one matches a YouTube video: watch it, clone the Lab, run it, make it
yours.

```bash
./scripts/lab youtube list                   # what's available
./scripts/lab youtube run vision_pick_place  # run one (cell + demo, in Docker)
```

## What a YouTube project is

A **vertical slice**: one concrete task, solved end-to-end on top of the Lab
cell you already have. It reuses the cell — robot description, MoveIt2,
controllers, camera, Gazebo — and adds only the few nodes that make *this* task
work. It is complete enough to be useful, and deliberately scoped to one task.

Each project is an ordinary ROS2 package under `src/`, named `yt_<something>`,
carrying a `youtube.yaml` manifest. Nothing here is a separate workspace: the
Lab's single `colcon build` builds these packages too, and `./scripts/lab
youtube` discovers them from their manifests.

```
src/yt_vision_pick_place/
├── youtube.yaml        # id, title, launch, minimum_edition, scope
├── README.md           # what it does, how to run, exercises, limitations
├── package.xml / CMakeLists.txt
├── launch/  config/  src/  scripts/
```

## The one rule: Free stays Free

A YouTube project must build and run on the **lowest edition it targets**
(usually the free Starter). It may depend only on capabilities that edition
ships — never on the paid application layers (`industrial_bt_framework`,
`lrwros_ur5_ik`, `lrwros_3d_cv`, the Behavior-Tree packages, hardware
bridges). The boundary guard checks this; see
[YOUTUBE_CONTENT_STRATEGY](../course/YOUTUBE_CONTENT_STRATEGY.md) (internal) for
the why.

The short version: a YouTube demo shows that **a task works**. The paid
Simulation and Full Tracks teach how to **engineer a reusable system** — skills,
orchestration, recovery, configuration, and sim-to-real. A demo is free; the
engineering is the product.

## Add a new project

Copy `src/yt_vision_pick_place/` as your starting point — it is the reference
implementation. Then see
[PROJECT_TEMPLATE/README.md](PROJECT_TEMPLATE/README.md) for the checklist.

## Available projects

| ID | Title | Min edition |
|---|---|---|
| `vision_pick_place` | Vision-Guided Pick and Place | starter |

_(This table mirrors what `./scripts/lab youtube list` prints.)_
