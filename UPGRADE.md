# Upgrade

You have a working industrial cell. What you do not have is an **application** —
and the reasoning that makes one survive contact with reality.

That is what the paid tracks are.

---

## What you have (free)

The Docker environment, the UR5 + Robotiq + depth-camera workcell, MoveIt2
planning you can drive from RViz, and the practice guide. A real cell, running.

**What it cannot do:** decide what to pick, find it with the camera, sequence a
grasp, recover from failure, or move to a different robot without a rewrite.

---

## Simulation Track

**Modules 0–8, plus the custom-robot / URDF elective.** Everything is simulated —
no hardware, ever.

You build the application on the cell you already have:

| | |
|---|---|
| **Module 0–2** | orientation, ROS2 foundations on this cell, and the Docker workflow |
| **Module 3–4** | the cell in depth: `ros2_control`, MoveIt2, planning groups, controllers |
| **Module 5** | **blind pick-and-place** — your first complete application |
| **Module 6** | **vision-guided pick-and-place** — a depth camera finds the object |
| **Module 7** | **the Behavior Tree architecture** — the same task rebuilt on a robot-agnostic framework |
| **Module 8** | **your capstone** — you design and build your own application |
| **Elective** | **build your own robot from scratch** — URDF from primitive cylinders to `ros2_control` |

The turn is Module 7. Modules 5 and 6 give you a working application; Module 7
shows you why the obvious way to write it does not scale, and rebuilds it on a
framework where the task is data and the robot is a plugin.

**You get:** guided lessons on Teachable + access to the private
`industrial_ros2_manipulation_lab_simulation` repository.

## Full Track

**Everything in Simulation, plus Module 9 — simulation to reality.**

The same architecture, the same Behavior Trees, the same task, deployed on a
**real industrial cell**:

- a **Fairino FR3WML** cobot with a soft gripper and a suction cup
- an **Intel RealSense** depth camera
- a **Jetson Orin Nano** running YOLO and 6D pose estimation
- hand-eye calibration, a vendor driver bridge, and the failures that come with real hardware
- plus the **xArm6 + local LLM (Ollama)** elective — driving a robot with a sentence in English

**You do not need to own any of that hardware.** Module 9 is designed to be
studied without it: the code is there to read, every architectural decision is
explained, and the whole point is what *did not* change between simulation and
reality — the framework, the trees, the task. Only the bottom layers were
swapped.

That is the course's thesis, and Module 9 is the proof.

**You get:** everything in the Simulation Track + access to the private
`industrial_ros2_manipulation_lab_full` repository.

---

## Which one

| If you want to... | Take |
|---|---|
| Build robotics applications properly, in simulation | **Simulation Track** |
| Also know what happens when it has to run on a real machine | **Full Track** |
| Just run a cell and experiment | **stay here** — the Starter Edition is genuinely yours |

Most people should start with the Simulation Track. Module 9 only means
something once you have built the thing it deploys.

## How access works

1. Purchase on Teachable.
2. **Submit your GitHub username** — there is a lesson in the course for this.
3. You are added to the private repository for your track. During the beta this
   is done by hand, **within 24 hours**.
4. Clone it and keep going.

The lessons live on Teachable. The lab lives on GitHub. You need both — which is
why the repository access is part of the product, not an extra.

## Free either way

**Module 0 is free on Teachable** and works against this edition. If you are not
sure yet, do Module 0 and the [PRACTICE_GUIDE.md](PRACTICE_GUIDE.md) exercises
first. Nothing here expires.

---

**Learn Robotics with ROS** — <https://learn-robotics-with-ros-s-school.teachable.com>
