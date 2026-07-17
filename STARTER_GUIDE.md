# Starter Guide — from clone to a moving robot

Target: **a UR5 planning and moving on your screen**, in under an hour, with no
ROS2 installed on your machine.

If something here does not work, it is almost always Docker. That has its own
guide: [docs/docker_troubleshooting.md](docs/docker_troubleshooting.md).

---

## 0. Before you start

| You need | Why |
|---|---|
| Ubuntu 22.04, or Windows 11 + WSL2 | the Gazebo GUI needs a Linux graphics stack |
| Docker Engine + the Compose plugin | the lab runs entirely inside a container |
| ~20 GB free disk | the ROS2 desktop-full image is large |
| A GPU is *not* required | but it makes Gazebo far more pleasant |

Set up your platform first:
- **Windows 11 + WSL2** → [docs/windows_wsl2_setup.md](docs/windows_wsl2_setup.md)
- **Ubuntu 22.04** → [docs/ubuntu_setup.md](docs/ubuntu_setup.md)

## 1. Check your machine

```bash
./scripts/lab doctor
```

It checks Docker, Compose, and whether a GUI application from inside a container
can reach your display. **Fix anything it complains about before building** — a
build on a broken environment just takes 30 minutes to fail.

## 2. Build, once

```bash
./scripts/lab build
```

This does two things:

1. **Builds the Docker image**: ROS2 Humble, Gazebo, MoveIt2, `ros2_control`.
2. **Fetches third-party sources** into `src/external/` with `vcs import`, from
   `.repos/simulation_dependencies.repos` — Universal Robots' UR5 description,
   PickNik's Robotiq gripper, IFRA-Cranfield's LinkAttacher. Then it builds the
   workspace with `colcon`.

> **Why are those not in the repo?** They belong to other people and they have
> their own release cycles. Vendoring someone else's robot description means
> silently shipping a stale fork of it. Fetching it by version is what a real
> project does — and it is why `.repos/simulation_dependencies.repos` matters
> more than its size suggests: **delete it and nothing works.**

First run takes 15–30 minutes. After that it is cached.

## 3. Verify

```bash
./scripts/lab check starter
```

Every line is a real check: Docker reachable, image built, sources fetched,
workcell package present, launch file present. **Do not skip this** — it turns
"it did not work" into a specific sentence.

## 4. Start the cell

```bash
./scripts/lab start module_03
```

You should get:

- **Gazebo** — a UR5 on a bench, a Robotiq 2F gripper, a depth camera, a table, an object
- **RViz** — the robot model, TF frames, and the MoveIt Motion Planning panel
- a terminal full of ROS2 node output

Stop it with `Ctrl+C`.

## 5. Prove it is real

Do this before anything else — it is the moment the cell stops being a picture:

1. In **RViz**, find the **MotionPlanning** panel.
2. Drag the orange interactive marker at the gripper to a new pose.
3. Click **Plan**. A ghost arm shows the trajectory it found.
4. Click **Execute**. **The arm moves in Gazebo.**

That is MoveIt2 planning a collision-free path, `ros2_control` executing it, and
Gazebo simulating the physics. It is the same stack that drives real industrial
arms — including the real FR3WML cobot in the Full Track.

## 6. Look inside

The container is yours:

```bash
./scripts/lab exec bash          # a shell inside the running lab

# then, inside:
ros2 node list                   # who is running
ros2 topic list                  # what they are saying
ros2 topic echo /joint_states    # where the robot thinks it is
ros2 control list_controllers    # which controllers are active
```

If `ros2 control list_controllers` shows controllers as **active**, your cell is
genuinely healthy.

---

## What you are looking at

```
  Gazebo            physics, the world, the sensors
     |
  ros2_control      controllers: the arm's joints, the gripper
     |
  MoveIt2           planning: "get the tool there without hitting anything"
     |
  RViz              your window into TF, the model, and the plan
```

[docs/architecture.md](docs/architecture.md) walks it in more detail.

## What is not here

The Starter Edition ships the **cell**. It does not ship the **application** —
nothing here decides *what* to pick, or *where* to put it.

That is not an oversight; it is the product. Building that application, in a way
that survives a change of robot, gripper or camera, is what the Simulation Track
teaches: blind pick-and-place → vision-guided → a Behavior Tree architecture →
your own capstone.

Ask for one of those modules and the lab will tell you so, politely:

```bash
$ ./scripts/lab start module_05
[lab] Module 05 (Blind Pick-and-Place) is available in the Simulation Track.
...
```

## Next

**[PRACTICE_GUIDE.md](PRACTICE_GUIDE.md)** — five exercises on the cell you just
started, and how to build yourself a sandbox without breaking it.
