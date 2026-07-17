# Architecture — Starter Edition

How the cell you just launched is put together, and why each layer is there.

This is the **Starter Edition** view: it describes the *cell* — the thing that
ships here. The architecture of the **application** that runs on top of it (how a
robot decides what to pick, and how that survives changing the robot) is what the
Simulation Track teaches. See [../UPGRADE.md](../UPGRADE.md).

---

## The stack

```
  ┌─────────────────────────────────────────────┐
  │  RViz            your window: model, TF, planning
  ├─────────────────────────────────────────────┤
  │  MoveIt2         "get the tool there without hitting anything"
  ├─────────────────────────────────────────────┤
  │  ros2_control    controllers: joints, gripper, joint states
  ├─────────────────────────────────────────────┤
  │  Gazebo          physics, the world, the simulated camera
  └─────────────────────────────────────────────┘
                    all inside one Docker container
```

Each layer talks to the one below through a **standard ROS2 interface**, not
through a private arrangement. That is the whole reason this is worth learning
rather than just running.

## The layers, and what each one owns

### Gazebo — the world

Physics, the table, the object, the pallet, and a simulated depth camera. It
loads the robot from the URDF and simulates what a real cell would do.

It publishes `/joint_states` (where the joints actually are) and camera topics.

### `ros2_control` — the joints

Between "a plan exists" and "the arm moved" sits a controller. This cell runs:

| Controller | Job |
|---|---|
| `joint_state_broadcaster` | publishes `/joint_states` — where the robot is |
| a trajectory controller | executes a `FollowJointTrajectory` goal on the arm |
| a gripper controller | opens and closes the Robotiq |

Check them any time:

```bash
./scripts/lab exec bash
ros2 control list_controllers    # all should say: active
```

**The important idea:** the hardware behind these controllers is declared in one
line of the URDF. Here it names a Gazebo plugin. On a real robot it names a
vendor driver. **Nothing above this line changes.** That single fact is what the
Full Track's Module 9 spends its time proving.

### MoveIt2 — the planning

Given a pose for the tool, MoveIt2 searches for a collision-free path to it. It
knows the robot's shape (from the URDF) and the world's obstacles (the planning
scene), and it hands the result to `ros2_control` as a trajectory.

Planning is a **search**, not a formula: it can fail, it takes time, and two runs
give two different paths. Exercise 3 in [../PRACTICE_GUIDE.md](../PRACTICE_GUIDE.md)
makes you feel this in ten minutes.

### RViz — the view

Not a simulator. RViz draws what other nodes publish: the model, the TF tree, the
planning scene, the proposed path. **If something looks wrong in RViz, the bug is
upstream of RViz** — that habit alone will save you days.

## What runs where

```
Your machine ──► Docker container ──┬── Gazebo      (physics + sensors)
                                    ├── ros2_control (controllers)
                                    ├── move_group   (MoveIt2 planning)
                                    ├── robot_state_publisher (URDF -> TF)
                                    └── RViz         (the window)
```

One container, one ROS2 graph. Your machine only provides Docker and a display.

## Where the packages live

| Package | What it is |
|---|---|
| `src/lrwros_ur5_workcell` | **the cell**: URDF, world, controller config, RViz layout |
| `src/lrwros_bringup` | **the launch layer**: `module_03.launch.py` starts everything above |
| `src/external/` | third-party sources, **fetched at build time** — not committed |

### Why `src/external/` is empty until you build

Universal Robots' UR5 description, PickNik's Robotiq driver and IFRA-Cranfield's
LinkAttacher are other people's code, with their own releases. Vendoring them
means shipping a silent fork of someone else's robot.

Instead, `.repos/simulation_dependencies.repos` names them **by version**, and
`./scripts/lab build` fetches them with `vcs import`.

> **That file is small and load-bearing.** Delete it and the cell cannot be
> built — there is no UR5 to load. It is the one file in this repository you
> should not touch until you understand it.

## The data flow, once

When you press **Execute** in RViz:

```
RViz  ──goal──►  MoveIt2  ──plan──►  ros2_control  ──►  Gazebo
                                                          │
                    /joint_states ◄──────────────────────┘
                          │
                          ▼
                robot_state_publisher ──/tf──► RViz  (the arm you see moving)
```

Note the loop: nothing "tells RViz" the arm moved. Gazebo publishes joint states,
`robot_state_publisher` turns them into TF, and RViz draws TF. **Every consumer
is decoupled from the source.**

Which is exactly why the same RViz, the same MoveIt2 and the same
`robot_state_publisher` work unchanged when the joint states come from a real
robot's encoders instead of a physics engine.

---

## What is deliberately not in this document

How to build an **application** on this cell — the layer that decides *what* to
do — is the subject of the paid tracks:

- **Simulation Track** — blind pick-and-place, vision-guided pick-and-place, and
  the Behavior Tree architecture that makes the task data instead of code
- **Full Track** — the same architecture on a real Fairino FR3WML cobot

The cell you have is the foundation both are built on. See
[../UPGRADE.md](../UPGRADE.md).
