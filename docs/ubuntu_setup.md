# Ubuntu 22.04 Setup — Docker and VS Code

The official native-Ubuntu guide for the Industrial ROS2 Manipulation Lab. Follow
it top to bottom and you will end with a UR5 workcell planning and moving in Gazebo
and RViz.

**No native ROS2 installation is required for the main path.** ROS2 Humble,
Gazebo, MoveIt2, `ros2_control` and every lab dependency live inside Docker
containers. Gazebo and RViz display through your X server.

> On **Windows 11**, do not use this guide — use
> [windows_wsl2_setup.md](windows_wsl2_setup.md). This one is for a machine
> running Ubuntu 22.04 directly (or dual-boot).

---

## What this guide installs

| Layer | What it is | Where it runs |
|---|---|---|
| **Docker Engine + Compose** | the container engine | Ubuntu, from Docker's repo |
| **ROS2 / Gazebo / MoveIt2** | the robot software | inside Docker |
| **VS Code** | reading and editing the code (recommended) | Ubuntu |

- Ubuntu 22.04 is the supported release.
- **Do not install ROS2 natively.** It runs inside the containers.
- Use the **Docker Engine from Docker's official repository** (below), not the
  `docker.io` package — you need Compose v2 (`docker compose`).
- VS Code is recommended for reading and editing the code, but the primary
  workflow is always `./scripts/lab ...` from a terminal.

## Table of contents

- [Before you start](#before-you-start)
- [1. Install Docker Engine and Compose](#1-install-docker-engine-and-compose)
- [2. Run Docker without sudo](#2-run-docker-without-sudo)
- [3. Allow GUI windows (X11)](#3-allow-gui-windows-x11)
- [4. Install VS Code](#4-install-vs-code)
- [5. Clone the repository under /home](#5-clone-the-repository-under-home)
- [6. Run lab doctor](#6-run-lab-doctor)
- [7. Build the lab](#7-build-the-lab)
- [8. Run the environment check](#8-run-the-environment-check)
- [9. Launch Module 03](#9-launch-module-03)
- [10. Verify MoveIt2 Plan and Execute](#10-verify-moveit2-plan-and-execute)
- [11. Open a second ROS2 terminal](#11-open-a-second-ros2-terminal)
- [12. Test Starter feature gating](#12-test-starter-feature-gating)
- [Daily startup workflow](#daily-startup-workflow)
- [Troubleshooting](#troubleshooting)
- [Final checklist](#final-checklist)

---

## Before you start

You need:

- **Ubuntu 22.04**.
- `sudo` access (to install Docker).
- At least **20 GB free disk space** — the base image and workspace build are large.
- A working internet connection — the first build downloads several gigabytes.

A GPU is not required. Without GPU acceleration, Gazebo renders in software:
usable, not fast. This guide does not promise fast rendering.

---

## 1. Install Docker Engine and Compose

```bash
# Remove old versions if any
sudo apt-get remove -y docker docker-engine docker.io containerd runc 2>/dev/null

# Install from Docker's official repository
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
```

---

## 2. Run Docker without sudo

```bash
sudo usermod -aG docker $USER
# Log out and back in (or run: newgrp docker), then verify:
docker version
docker compose version
docker run --rm hello-world
```

**Expected output:**

- `docker version` shows both a `Client:` and a `Server:` section.
- `docker compose version` prints a Compose v2 version.
- `docker run --rm hello-world` prints `Hello from Docker!` — **without `sudo`**.

> Do not use `sudo docker` for the lab. If Docker only works with `sudo`, your
> user is not in the `docker` group yet — log out and back in after the
> `usermod` above. See [Troubleshooting](#troubleshooting).

---

## 3. Allow GUI windows (X11)

Gazebo and RViz run inside the container and draw on your X server. The compose
file mounts `/tmp/.X11-unix` and passes `DISPLAY`. Allow local containers to use
your X server:

```bash
xhost +local:
echo "$DISPLAY"          # should print something like :0 or :1
```

**Expected output:** `xhost` reports `LOCAL:` added; `$DISPLAY` is not empty.

> Run `xhost +local:` once per login session, or add it to your shell profile.
> On a **Wayland** session, XWayland usually handles it; if windows stay blank,
> log in with an "Ubuntu on Xorg" session from the login screen. See
> [docker_troubleshooting.md](docker_troubleshooting.md).

---

## 4. Install VS Code

Recommended for reading and editing the code — not required to run the lab.

1. Install VS Code (the `.deb` package or snap).
2. Install the **Dev Containers** extension.
3. Open the repository (after cloning it in the next section) with `code .`.

Optional: this repository ships a `.devcontainer/` configuration (service `lab`,
with ROS/Python/C++ extensions). **Command Palette → Dev Containers: Reopen in
Container** opens the lab container in the editor.

> Dev Containers is a code-editing convenience. It does **not** start Gazebo or
> RViz. The supported way to run the lab is `./scripts/lab ...` from a terminal.

---

## 5. Clone the repository under /home

```bash
cd ~
git clone https://github.com/LearnRoboticsWROS-Lab/industrial_ros2_manipulation_lab.git
cd industrial_ros2_manipulation_lab
pwd
git status --short
```

**Expected output:**

- `pwd` prints `/home/<linux-user>/industrial_ros2_manipulation_lab`.
- The public Starter repository clones **without** a GitHub username, password, or
  token.
- `git status --short` prints nothing (a clean checkout).

> If git asks you to authenticate while cloning the public Starter repository,
> stop — the public edition should not require it.

---

## 6. Run lab doctor

```bash
./scripts/lab doctor
```

**Expected output** (order may vary):

```
[lab] PASS  docker reachable (...)
[lab] PASS  docker compose v2 available
[lab] PASS  git available
[lab] PASS  running on native Linux
[lab] PASS  repository on a Linux filesystem (/home/<linux-user>/industrial_ros2_manipulation_lab)
[lab] PASS  DISPLAY is set (:0)
[lab] PASS  free disk space: NN GB
[lab] PASS  internet reachable
[lab] doctor: all checks passed.
```

If `doctor` warns that local containers may not open windows, run `xhost +local:`
(section 3).

> **Do not continue to the build until all doctor checks pass.**

---

## 7. Build the lab

```bash
./scripts/lab build
```

The first build:

- downloads the base image `osrf/ros:humble-desktop-full` (several gigabytes);
- imports the third-party dependencies (UR5 description, Robotiq gripper,
  IFRA LinkAttacher) with `vcs import` into `src/external/`, from
  `.repos/simulation_dependencies.repos`;
- builds the ROS2 workspace with `colcon` inside the container.

It can take tens of minutes, depending on your connection, CPU and disk. This
guide does not promise an exact time. Do not let the machine sleep mid-build.

---

## 8. Run the environment check

```bash
./scripts/lab check starter
```

**Expected output:** every line is `PASS`, ending with a pointer to
`./scripts/lab start module_03`.

> The `starter` check target exists in the free Starter Edition. In the paid
> editions, verify per module instead — for example `./scripts/lab check module_03`.

---

## 9. Launch Module 03

```bash
./scripts/lab start module_03
```

This launches the UR5 simulation workcell: Gazebo + MoveIt + RViz.

**Expected output:** two windows appear:

- **Gazebo**, with the UR5 arm, the Robotiq gripper, the simulated depth camera, a
  table/workcell, and the **pallet**.
- **RViz**, with the robot model, TF frames, and the **MotionPlanning** panel.

A black/empty Gazebo window on first start can simply be slow software rendering —
give it 30–60 seconds.

Stop it with `Ctrl+C` in the terminal that launched it.

---

## 10. Verify MoveIt2 Plan and Execute

With Module 03 running, in **RViz**:

1. Find the **MotionPlanning** panel.
2. Drag the interactive marker at the end-effector to a reachable pose.
3. Click **Plan** — a preview trajectory appears.
4. Click **Execute**.
5. **The robot moves in Gazebo** to match.

If the arm moves, the whole stack is validated:

```
Ubuntu 22.04 → Docker → ROS2 Humble → MoveIt2 → Gazebo → X11
```

---

## 11. Open a second ROS2 terminal

Leave Module 03 running in the first terminal and open a second one.

```bash
cd ~/industrial_ros2_manipulation_lab
./scripts/lab shell
```

`./scripts/lab shell` starts a **separate, temporary lab container** with ROS2
already sourced. It shares the host network and IPC namespace, so it joins the
**same ROS2 graph** as the running simulation — it can see the same topics and
their data. It is not the same container running Gazebo and RViz. Leave it with
`exit`; it is removed on exit (`--rm`).

**Inside the lab container:**

```bash
ros2 node list
ros2 topic list
ros2 control list_controllers      # the arm and gripper controllers must be: active
ros2 topic echo /joint_states
```

You can also run a single command without an interactive shell:

```bash
./scripts/lab exec ros2 node list
```

> If `ros2 topic list` shows the topics but `ros2 topic echo` receives nothing,
> see [Second Terminal Sees the Topics but Receives No Data](docker_troubleshooting.md#second-terminal-sees-the-topics-but-receives-no-data).

---

## 12. Test Starter feature gating

Paid modules are not part of the Starter Edition. They must fail cleanly — a clear
upgrade notice, never a traceback.

```bash
for c in module_05 module_06 module_07 module_09; do
  echo "════════ $c"
  ./scripts/lab start "$c" 2>&1 | head -8
done

./scripts/lab start --mode hardware 2>&1 | head -8
```

**Expected output:** clean upgrade notices. No Python traceback, no "package not
found", no "command not found", no hung process.

---

## Daily startup workflow

Every time you return to the lab:

```bash
xhost +local:                       # once per login session, for the GUI
cd ~/industrial_ros2_manipulation_lab
./scripts/lab doctor
./scripts/lab start module_03
```

You do **not** rebuild the image every time. Run `./scripts/lab build` again only
after you change the environment, or when an update requires it.

---

## Troubleshooting

### Gazebo or RViz does not appear

- Run `xhost +local:` and confirm `echo $DISPLAY` is not empty.
- A black window on first start is usually slow software rendering — wait 30–60 s.
- On Wayland, try an "Ubuntu on Xorg" login session.
- More detail: [docker_troubleshooting.md](docker_troubleshooting.md).

### Docker only works with sudo

Your user is not in the `docker` group yet:

```bash
sudo usermod -aG docker $USER
# then log out and back in (or: newgrp docker)
groups | grep docker        # 'docker' must appear
docker run --rm hello-world # must work without sudo
```

### "Cannot connect to the Docker daemon"

```bash
sudo systemctl start docker
sudo systemctl enable docker    # start it automatically on boot
```

### Nothing moves, or a module seems to fail

The application nodes start on a timer (module_05/06/07 wait 25–55 s) for Gazebo,
`move_group` and the controllers to come up. On a slower machine the timers can be
too short: the application starts before the controllers are active and finds no
action server. First, check the controllers:

```bash
./scripts/lab exec ros2 control list_controllers    # must all be: active
```

If they are not active, relaunch, or run the cell and the application in two
terminals so you control the timing yourself:

```bash
# terminal 1: the cell
./scripts/lab start module_03
# terminal 2: the application (once the controllers are active)
./scripts/lab exec ros2 run lrwros_ur5_ik pick_place
```

### A ros2_control_node crash in the log is expected

When you start a module you will see, in the log:

```
[ros2_control_node-...] terminate called after throwing an instance of 'pluginlib::LibraryLoadException'
[ros2_control_node-...] Aborted
```

**This is expected and harmless.** On Gazebo Classic the real controller_manager
runs inside the `gazebo_ros2_control` plugin (inside gzserver). A short-lived
standalone `ros2_control_node` is started only to let the controllers reach a
configurable state, and it cannot load the Gazebo hardware plugin outside Gazebo —
so it exits. What matters is not the absence of that message, but that the
controllers activate:

```bash
grep -c "Configured and activated" <(./scripts/lab start module_03 2>&1)   # should reach 3
```

or simply `ros2 control list_controllers` showing them `active`.

### Module 6 does not run the application by itself

That is by design. `module_06` starts the cell and the perception node, then stops
and prints a choice. Open a second terminal and pick one:

```bash
./scripts/lab exec ros2 run lrwros_ur5_ik pick_place_camera
#   or
./scripts/lab exec ros2 run lrwros_ur5_ik pick_place_choose_planner_camera
```

Modules 5 and 7 start their application for you; Module 6 asks.

### Rebuilding from scratch

```bash
docker compose -f docker/compose.yaml down --remove-orphans
rm -rf build/ install/ log/
./scripts/lab build
```

### Optional: NVIDIA GPU acceleration

Only needed if Gazebo feels slow. Install `nvidia-container-toolkit`, then enable
the commented GPU section in `docker/compose.yaml`. The lab is designed to work
with CPU rendering too.

---

## Final checklist

- [ ] Ubuntu 22.04
- [ ] Docker Engine installed from Docker's repo
- [ ] `docker version` shows Client and Server
- [ ] `docker compose version` works
- [ ] `docker run --rm hello-world` works without `sudo`
- [ ] `xhost +local:` run (GUI allowed)
- [ ] repository cloned under `/home`
- [ ] public repository cloned without credentials
- [ ] `./scripts/lab doctor` all PASS
- [ ] `./scripts/lab build` completes
- [ ] `./scripts/lab check starter` all PASS
- [ ] `./scripts/lab start module_03` launches
- [ ] Gazebo appears
- [ ] RViz appears
- [ ] the pallet is visible
- [ ] the MotionPlanning panel is available
- [ ] Plan + Execute moves the robot
- [ ] a second terminal sees the ROS2 graph
- [ ] controllers show `active`
- [ ] paid commands return clean upgrade notices

When every box is ticked, your Ubuntu environment is validated end to end.
