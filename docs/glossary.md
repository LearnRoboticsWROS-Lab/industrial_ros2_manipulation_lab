# Glossary

Practical definitions, in the sense used by this lab. Terms link to where you
meet them first.

**Action (ROS2)** — Long-running request with feedback and result (e.g.
`/task/pick_place`). Used when a service would block too long. (Module 1, 7)

**Behavior Tree (BT)** — A tree of small, reusable behavior nodes (sequences,
fallbacks, actions, conditions) that orchestrates an application. Replaces the
"one big script" for industrial task logic. (Module 7)

**Blind pick-and-place** — Pick-and-place with hardcoded/configured poses, no
perception. The correct first milestone. (Module 5)

**Bridge (robot/gripper bridge)** — The one package that speaks the vendor
protocol of a real robot/gripper and exposes standard ROS2 interfaces. Driver-
specific code lives here and only here. (Module 9)

**colcon** — The ROS2 build tool (`colcon build` builds every package in `src/`).

**Dev Container** — VS Code feature that opens your workspace inside the lab's
Docker container with extensions preconfigured. (`.devcontainer/`)

**Depth camera / point cloud** — Camera producing per-pixel distance; the
simulated one publishes `/camera/points` (PointCloud2). (Modules 3, 6)

**DDS / ROS_DOMAIN_ID** — The middleware under ROS2 topics; the domain id
isolates ROS2 systems sharing a network.

**End effector / TCP** — The tool mounted on the robot flange (our Robotiq
gripper); TCP = tool center point, the frame motion targets refer to.

**Gazebo (Classic)** — The physics simulator used by the lab; the workcell world
lives in `lrwros_ur5_workcell`. (Module 3)

**GripperCommand action** — Standard interface of the gripper action controller;
the sim backend of `/gripper/command` uses it. (Module 4)

**Hand-eye calibration** — Estimating the transform between camera and robot so
detections can be expressed in the robot base frame. Simulated cells know it by
construction; real cells must calibrate. (Modules 6, 9)

**Intrinsics** — Camera parameters (fx, fy, cx, cy) mapping pixels to rays; used
to reconstruct 3D points from depth. Published on `/camera/camera_info`. (Module 6)

**IK (inverse kinematics)** — Joint angles for a desired TCP pose; solved through
MoveIt2 in this lab. (Module 4)

**Launch file** — Python file starting a set of nodes with parameters
(`lrwros_bringup/launch/`). (Module 1)

**LinkAttacher** — Gazebo plugin that welds/detaches two links at runtime; the
lab's simulated grasping mechanism. (Modules 3, 4)

**Mock mode** — Running the application against fake motion/perception backends,
no Gazebo. Same interfaces, instant startup. (Modules 1, 7)

**MoveIt2** — The manipulation planning framework: scene, kinematics, planners,
`MoveGroupInterface`. Configured in `lrwros_ur5_moveit_config`. (Module 4)

**Node** — A ROS2 process participating in the graph. (Module 1)

**OctoMap** — 3D occupancy map MoveIt builds from the point cloud for collision-
aware planning. (Modules 4, 6)

**Package** — The ROS2 unit of code/build/dependency (`package.xml`). (Module 1)

**Parameter (ROS2)** — Named runtime configuration of a node; the lab keeps task
poses and object lists in YAML parameter files. (Module 1)

**Perception mock** — Node publishing detections from config/replay instead of a
camera; lets you develop application logic with zero hardware. (Modules 6, 7)

**PickPlace action** — The lab's application-level contract:
`/task/pick_place` in `lrwros_interfaces`. (Module 7)

**ros2_control** — The controller framework between planners and (simulated or
real) actuators: controller manager + controllers (joint trajectory, gripper,
…). (Module 4)

**RViz** — ROS2 3D visualization tool: robot state, planning scene, TFs, point
clouds. Not a simulator — Gazebo simulates, RViz displays.

**Service (ROS2)** — Synchronous request/response (e.g. `/motion/move_to_pose`).
(Module 1)

**SRDF** — Semantic robot description for MoveIt: planning groups, named states
(`home`), collision exclusions. (Module 4)

**TF / TF2** — The transform system tracking frames over time (`world`,
`base_link`, `tool0`, `camera_link`…). Most vision bugs are TF bugs. (Modules 3, 6)

**Topic** — Named many-to-many data stream (e.g. `/camera/points`,
`/perception/detections`). (Module 1)

**URDF / Xacro** — Robot description format / its macro language. The workcell
xacro composes UR5 + gripper + camera + stand. (Module 3, elective)

**vcs / .repos file** — vcstool imports pinned third-party repositories listed in
`.repos/*.repos` into `src/` — the lab's way of not vendoring third-party code.

**Vision-guided pick-and-place** — Pick poses computed from perception at
runtime instead of configured constants. (Module 6)

**Workspace (ROS2)** — A folder with `src/` built by colcon producing
`install/` (the overlay you `source`). This repository is one workspace.

**YOLO** — Real-time object detection family used in the Module 9 case study on
the Jetson.

**6D pose** — Position + orientation of an object (x, y, z, roll, pitch, yaw);
what real grasping ultimately needs. (Modules 6, 9)
