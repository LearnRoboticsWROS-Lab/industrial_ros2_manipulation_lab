# Industrial ROS2 Manipulation Lab — Starter Edition

A **runnable industrial robot cell**: a UR5 with a Robotiq gripper and a depth
camera, in Gazebo, with MoveIt2 and RViz — running inside Docker on Ubuntu 22.04
or Windows 11 + WSL2.

Clone it, build it once, and a robot arm plans and moves on your machine.

```bash
git clone https://github.com/LearnRoboticsWROS-Lab/industrial_ros2_manipulation_lab.git
cd industrial_ros2_manipulation_lab
./scripts/lab doctor          # is my machine ready?
./scripts/lab build           # build the image + workspace (first run: ~15-30 min)
./scripts/lab start module_03 # Gazebo + MoveIt + RViz, with the cell in it
```

**No native ROS2 installation required.** ROS2 Humble, Gazebo, MoveIt2 and
`ros2_control` all live in the container. Your machine only needs Docker.

---

## What this is

This is the **free Starter Edition** of a larger product. It is deliberately not
a demo video or a screenshot repo: it is the real environment, and the cell in it
is the same cell the full course builds on.

**What you get here:**

- the Docker environment — ROS2 Humble, Gazebo, MoveIt2, `ros2_control`
- the UR5 + Robotiq + depth-camera workcell, running
- MoveIt2 motion planning you can drive from RViz
- setup guides for Windows 11 + WSL2 and Ubuntu 22.04
- a practice guide, so the cell is something you *use*, not just something you launch

**What you do not get here — and this is the honest part:**

This edition gives you the **cell**. It does not give you the **application** on
top of it, or the course that teaches you to build one. Those are the paid tracks:

| | |
|---|---|
| **Simulation Track** | blind pick-and-place → vision-guided pick-and-place → a Behavior Tree architecture → your own capstone. Modules 0–8, plus the custom-robot / URDF elective. |
| **Full Track** | everything in Simulation, plus **simulation-to-real**: the same architecture deployed on a real Fairino FR3WML cobot with a RealSense camera and a Jetson Orin Nano running YOLO and 6D pose estimation. Plus an xArm6 + local-LLM elective. |

See **[UPGRADE.md](UPGRADE.md)**.

The guided lessons live on **Teachable**; this repository is the lab they teach
you to use. **Module 0 is free** — you can follow it against this edition today.

## Supported platforms

| Platform | Status | Guide |
|---|---|---|
| Ubuntu 22.04 | supported | [docs/ubuntu_setup.md](docs/ubuntu_setup.md) |
| Windows 11 + WSL2 | supported | [docs/windows_wsl2_setup.md](docs/windows_wsl2_setup.md) |
| macOS | not supported | GPU-accelerated Gazebo GUI does not work reliably |

Docker problems are the most common blocker for new users — they have their own
guide: [docs/docker_troubleshooting.md](docs/docker_troubleshooting.md).

## Commands

| Command | What it does |
|---|---|
| `./scripts/lab doctor` | checks Docker, the GUI setup and your environment |
| `./scripts/lab build` | builds the image and the ROS2 workspace |
| `./scripts/lab start module_03` | launches the workcell: Gazebo + MoveIt + RViz |
| `./scripts/lab check starter` | verifies your setup, item by item |

Ask for a paid module (`./scripts/lab start module_05`) and the lab tells you
what that module is and where to get it. **It will not throw a traceback at you.**

## Where to go next

1. **[STARTER_GUIDE.md](STARTER_GUIDE.md)** — get the cell running, and know what you are looking at.
2. **[PRACTICE_GUIDE.md](PRACTICE_GUIDE.md)** — five exercises that turn it from a demo into practice, and how to build a sandbox without breaking the core.
3. **[docs/architecture.md](docs/architecture.md)** — how the cell is put together.
4. **[UPGRADE.md](UPGRADE.md)** — when you are ready to build the application.

## A note on what "free" means here

The Starter Edition is not crippled software with a countdown. It is a working
industrial cell that took a long time to make work, and it is genuinely yours to
use, study, break and rebuild.

What is paid is the part that is hard to get anywhere else: **the architecture,
and the reasoning behind it** — how to build an application that survives a
robot swap, a gripper change, a camera you did not plan for, and the day the
simulation has to become a real machine on a real bench.

## Licence

Apache-2.0 — see [LICENSE](LICENSE).

Third-party components are fetched at build time from their own repositories
(`.repos/simulation_dependencies.repos`) and keep their own licences: Universal
Robots' ROS2 description, PickNik's Robotiq gripper driver, IFRA-Cranfield's
LinkAttacher.
