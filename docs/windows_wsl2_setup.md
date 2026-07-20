# Windows 11 Setup — WSL2, Docker Desktop and VS Code

The official Windows 11 guide for the Industrial ROS2 Manipulation Lab. Follow it
top to bottom on a fresh machine and you will end with a UR5 workcell planning and
moving in Gazebo and RViz, shown as normal Windows windows.

**No native ROS2 installation is required.** ROS2 Humble, Gazebo, MoveIt2,
`ros2_control` and every lab dependency live inside Docker containers. WSL2
provides the Linux environment; WSLg displays the GUI on Windows.

---

## What this guide installs

| Layer | What it is | Where it runs |
|---|---|---|
| **WSL2** | the Linux kernel and environment | Windows feature |
| **Ubuntu 22.04** | the Linux distribution the lab is built for | inside WSL2 |
| **WSLg** | shows Linux GUI windows as Windows windows | ships with WSL |
| **Docker Desktop** | the container engine, WSL2 backend | Windows app |
| **ROS2 / Gazebo / MoveIt2** | the robot software | inside Docker |
| **VS Code** | reading and editing the code (recommended) | Windows app |

### Supported and unsupported paths

- **Windows 11** is the supported Windows platform.
- **Docker Desktop is required.** This guide does not support installing a Docker
  Engine directly inside WSL/Ubuntu. Use Docker Desktop with the WSL2 backend.
- **Do not install ROS2 natively on Windows.**
- **Do not install ROS2 natively inside Ubuntu/WSL.**
- **VS Code is strongly recommended** for reading and editing the code, but it is
  not required to launch the lab — the primary workflow is always
  `./scripts/lab ...` from an Ubuntu terminal.

---

## Table of contents

- [Before you start](#before-you-start)
- [PowerShell vs Ubuntu / WSL](#powershell-vs-ubuntu--wsl)
- [1. Update WSL](#1-update-wsl)
- [2. Install Ubuntu 22.04 explicitly](#2-install-ubuntu-2204-explicitly)
- [3. Verify Ubuntu and WSL2](#3-verify-ubuntu-and-wsl2)
- [4. Verify WSLg with xeyes](#4-verify-wslg-with-xeyes)
- [5. Install Docker Desktop](#5-install-docker-desktop)
- [6. Enable Docker Desktop WSL Integration](#6-enable-docker-desktop-wsl-integration)
- [7. Verify Docker without sudo](#7-verify-docker-without-sudo)
- [8. Verify Windows interoperability](#8-verify-windows-interoperability)
- [9. Install VS Code](#9-install-vs-code)
- [10. Clone the repository under /home](#10-clone-the-repository-under-home)
- [11. Run lab doctor](#11-run-lab-doctor)
- [12. Build the lab](#12-build-the-lab)
- [13. Run Starter checks](#13-run-starter-checks)
- [14. Launch Module 03](#14-launch-module-03)
- [15. Verify MoveIt2 Plan and Execute](#15-verify-moveit2-plan-and-execute)
- [16. Open a second ROS2 terminal](#16-open-a-second-ros2-terminal)
- [17. Test Starter feature gating](#17-test-starter-feature-gating)
- [Daily startup workflow](#daily-startup-workflow)
- [Troubleshooting](#troubleshooting)
- [Final checklist](#final-checklist)

---

## Before you start

You need:

- **Windows 11** (WSLg requires Windows 11, or Windows 10 22H2 with recent updates).
- Administrator access (to install WSL and Docker Desktop).
- At least **20 GB free disk space** — the base image and the workspace build are large.
- A working internet connection — the first build downloads several gigabytes.

A GPU is not required. Without GPU passthrough, Gazebo renders in software: usable,
not fast. This guide does not promise native performance.

Set aside about an hour. Most of it is the first build downloading and compiling —
you do not have to watch it.

---

## PowerShell vs Ubuntu / WSL

You will use **two different terminals**. Confusing them is the most common cause
of "the command does not exist". Every command block in this guide is labelled
with the terminal it belongs to.

**PowerShell** — the Windows terminal.

- Manages WSL itself.
- Runs commands like `wsl --install`, `wsl --update`, `wsl --shutdown`.
- Starts a distribution with `wsl -d Ubuntu-22.04`.

**Ubuntu / WSL** — the Linux shell.

- Runs `apt`, `git`, `docker`, `code` and `./scripts/lab`.
- Is where you do all the lab work.
- Does **not** run the command `wsl` — that is a Windows command, and it does not
  exist as a Linux program. If you type `wsl -d Ubuntu-22.04` inside Ubuntu, that
  is the wrong terminal.

**Inside the lab container** — a shell you open with `./scripts/lab shell`. ROS2
is already available there. Covered in section 16.

The normal way to open the Linux shell is from PowerShell:

**PowerShell:**

```powershell
wsl -d Ubuntu-22.04
```

Then, inside Ubuntu:

**Ubuntu / WSL:**

```bash
cd ~/industrial_ros2_manipulation_lab
./scripts/lab doctor
```

---

## 1. Update WSL

Open **PowerShell as Administrator** (right-click Start → *Terminal (Admin)*).

**PowerShell (Administrator):**

```powershell
wsl --install
wsl --update
```

`wsl --update` installs or refreshes the WSL kernel and **WSLg**, the component
that displays Linux GUI windows (Gazebo, RViz) as Windows windows.

**Reboot Windows** after this. WSLg does not fully activate until you restart.

After the reboot, confirm WSLg is present:

**PowerShell:**

```powershell
wsl --version
```

**Expected output:** the list includes a line such as `WSLg version: 1.x.x`. If
there is no WSLg line, the GUI will not work — run `wsl --update` again and reboot.

> **Do not rely on `wsl --install` alone to give you the right Ubuntu.** On its
> own it installs whatever the current default Ubuntu is, which may not be 22.04.
> The next section installs the correct version explicitly.

---

## 2. Install Ubuntu 22.04 explicitly

The lab is built and tested on **Ubuntu 22.04**. A different version is not a
supported environment.

**PowerShell:**

```powershell
wsl --list --online
wsl --install -d Ubuntu-22.04
wsl --set-default Ubuntu-22.04
```

The first time Ubuntu-22.04 starts, it asks you to create a **Linux username and
password**. These are separate from your Windows account. Remember them.

> ⚠️ **The generic Ubuntu distribution may not be 22.04.** Installing the generic
> "Ubuntu" (without `-d Ubuntu-22.04`) can pull a newer release — for example
> Ubuntu 26.04, codename *resolute*, or Ubuntu 24.04. **That is not the lab
> environment.** Always install `Ubuntu-22.04` explicitly, and always set it as
> the default with `wsl --set-default Ubuntu-22.04`.
>
> If you already installed the wrong distribution, you may leave it in place — just
> make sure **Ubuntu-22.04** is the default. Do not rush to `wsl --unregister` the
> wrong one: `wsl --unregister <name>` **permanently deletes** that distribution's
> data, with no undo.

---

## 3. Verify Ubuntu and WSL2

**PowerShell:**

```powershell
wsl -l -v
```

**Expected output:** a line with an asterisk `*` next to `Ubuntu-22.04`, and
`VERSION` equal to `2`:

```
  NAME              STATE           VERSION
* Ubuntu-22.04      Running         2
```

Now open the Linux shell and confirm the release from inside it.

**PowerShell:**

```powershell
wsl -d Ubuntu-22.04
```

**Ubuntu / WSL:**

```bash
cat /etc/os-release
uname -r
```

**Expected output:** `cat /etc/os-release` shows

```
VERSION_ID="22.04"
VERSION_CODENAME=jammy
```

and `uname -r` prints a kernel containing:

```
microsoft-standard-WSL2
```

> **Stop here if you see Ubuntu 24.04, Ubuntu 26.04, or any codename other than
> `jammy`.** The distribution name must be `Ubuntu-22.04` and `VERSION_ID` must be
> `22.04`. Go back to section 2 and install the correct version.

---

## 4. Verify WSLg with `xeyes`

Test the GUI **before** downloading a multi-gigabyte image. If windows cannot
display, there is no point building first and discovering it later.

**Ubuntu / WSL:**

```bash
sudo apt update
sudo apt install -y x11-apps git
xeyes
```

**Expected output:** a small window with **two eyes that follow your mouse**,
appearing as a normal Windows window.

- ✅ **You see the eyes** → WSLg works. Close the window and continue.
- ❌ **No window, or an error about `DISPLAY`** → WSLg is not active.
  - From **PowerShell**: `wsl --update`, then `wsl --shutdown`.
  - Reboot Windows if needed.
  - Re-open Ubuntu and run `xeyes` again.
  - **Do not start the build until `xeyes` opens.**

Optional diagnostics, inside Ubuntu:

**Ubuntu / WSL:**

```bash
echo "$DISPLAY"
echo "$WAYLAND_DISPLAY"
```

`DISPLAY` is usually `:0`; `WAYLAND_DISPLAY` is usually `wayland-0`. Empty values
mean WSLg is not wired up yet.

---

## 5. Install Docker Desktop

Docker Desktop is the container engine for the Windows path. Do **not** install a
Docker Engine inside Ubuntu.

1. Download **Docker Desktop for Windows** from docker.com and install it.
2. During or after install, make sure it uses the **WSL 2 based engine**
   (*Settings → General → Use the WSL 2 based engine*).
3. Start Docker Desktop and wait until it reports **Engine running**.

> **Docker Desktop does not always start automatically, and it does not always
> stay running.** After a Windows reboot, Resource Saver, `wsl --shutdown`, or
> closing the app, the engine may be stopped. If Docker Desktop shows a **Play**
> button and CPU/RAM at zero, the engine is stopped: press **Play** and wait for
> **Engine running** before using Docker in Ubuntu.

---

## 6. Enable Docker Desktop WSL Integration

Docker Desktop must expose Docker to your Ubuntu distribution.

1. Docker Desktop → **Settings** → **Resources** → **WSL Integration**.
2. Enable integration for **Ubuntu-22.04** explicitly.
3. Turn **off** integration for any other Ubuntu distributions you do not use
   (for example a wrong-version one from section 2).
4. Click **Apply & restart**.
5. Wait until Docker Desktop reports **Engine running** again.

---

## 7. Verify Docker without sudo

With Docker Desktop running and WSL integration enabled, Docker must work from
Ubuntu **without `sudo`**.

**Ubuntu / WSL:**

```bash
docker version
docker compose version
docker run --rm hello-world
```

**Expected output:**

- `docker version` shows **both** a `Client:` and a `Server:` section.
- `docker compose version` prints a Compose v2 version (note: `docker compose`,
  not `docker-compose`).
- `docker run --rm hello-world` prints `Hello from Docker!`.
- None of this needs `sudo`.

> **Do not use `sudo docker`.** If Docker only works with `sudo`, the setup is
> not correct for this lab, and `sudo` will hide the real problem. Instead check:
> Docker Desktop is open and shows **Engine running**; WSL Integration is enabled
> for **Ubuntu-22.04**; the Docker socket exists (`ls -l /var/run/docker.sock`);
> and you have **not** installed a second Docker Engine inside the distribution.
> Do not uninstall packages blindly — diagnose first (see
> [Troubleshooting](#troubleshooting)).

---

## 8. Verify Windows interoperability

This check is **separate and mandatory**, and it is easy to skip because
everything above can look fine while it is broken. WSL interoperability lets Linux
run Windows `.exe` programs. Docker Desktop relies on it — it uses Windows
executables (including a credential helper) during image pulls and builds. If
interop is broken, `docker run hello-world` and even `./scripts/lab doctor` can
still pass, and then the **build fails**.

**Ubuntu / WSL:**

```bash
cmd.exe /c echo WSL_INTEROP_OK
```

**Expected output:**

```
WSL_INTEROP_OK
```

Additional diagnostic:

**Ubuntu / WSL:**

```bash
ls -l /proc/sys/fs/binfmt_misc/WSLInterop
```

**Expected output:** the file exists (interop is registered).

> **Do not continue to the build if `cmd.exe` returns `Exec format error`.** That
> means interoperability is broken even if the Windows directories are on your
> `PATH`. Fix it first — see
> [Windows executables return Exec format error](#windows-executables-return-exec-format-error).

---

## 9. Install VS Code

VS Code is recommended for reading and editing the lab code. It is not required to
run the lab.

1. Install **Visual Studio Code on Windows** (not inside WSL — do not
   `apt install code`).
2. In VS Code, install two extensions:
   - **WSL** (`ms-vscode-remote.remote-wsl`)
   - **Dev Containers** (`ms-vscode-remote.remote-containers`)
3. Open the repository (after cloning it in the next section):

**Ubuntu / WSL:**

```bash
cd ~/industrial_ros2_manipulation_lab
code .
```

**Expected result:** VS Code opens with a green indicator in the bottom-left
corner reading **WSL: Ubuntu-22.04** (or equivalent). You are now editing files on
the Linux filesystem, through VS Code on Windows.

### Optional: Dev Containers

This repository ships a `.devcontainer/` configuration that opens the lab
container inside VS Code (service `lab`, ROS/Python/C++/YAML/CMake extensions). It
is useful for reading and editing code with ROS2 available in the editor.

If you want it: **Command Palette → Dev Containers: Reopen in Container**.

> Opening the Dev Container is a code-editing convenience, not the way you launch
> the simulation. Dev Containers does **not** start Gazebo or RViz. The primary,
> supported way to run the lab remains `./scripts/lab ...` from an Ubuntu terminal.

---

## 10. Clone the repository under /home

Clone **inside the Linux filesystem**, under `/home/<linux-user>`, not under
`/mnt/c`.

When you first open Ubuntu from a PowerShell window, the shell may start in
`/mnt/c/Users/<WindowsUser>`. That is normal — WSL inherits the Windows working
directory. Move to your Linux home first:

**Ubuntu / WSL:**

```bash
cd ~
pwd
```

**Expected output:** `/home/<linux-user>`.

Then clone:

**Ubuntu / WSL:**

```bash
git clone https://github.com/LearnRoboticsWROS-Lab/industrial_ros2_manipulation_lab.git
cd industrial_ros2_manipulation_lab
pwd
git status --short
```

**Expected output:**

- `pwd` prints `/home/<linux-user>/industrial_ros2_manipulation_lab`.
- The clone completes **without asking for a GitHub username, password, or token**.
- `git status --short` prints nothing (a clean checkout).

> **The public Starter repository must clone without credentials.** If git asks
> you to authenticate, stop — the public edition should not require it. Check the
> URL is correct and that you are cloning the public repository.

Why the Linux filesystem, and not `/mnt/c`: keeping the repository under
`/home/<linux-user>` avoids Windows/Linux permission mismatches, avoids repeatedly
crossing the Windows/Linux filesystem bridge, and gives Docker, `colcon` and file
watching a reliable place to work. It is the supported location.

Optional — open the current folder in Windows Explorer (only after interop is
verified in section 8):

**Ubuntu / WSL:**

```bash
explorer.exe .
```

---

## 11. Run lab doctor

From here on, all work is inside Ubuntu, in the repository folder.

**Ubuntu / WSL:**

```bash
./scripts/lab doctor
```

**Expected output** (order may vary):

```
[lab] PASS  docker reachable (...)
[lab] PASS  docker compose v2 available
[lab] PASS  git available
[lab] PASS  running inside WSL
[lab] PASS  repository on a Linux filesystem (/home/<linux-user>/industrial_ros2_manipulation_lab)
[lab] PASS  WSLg present — GUI applications will display as Windows windows
[lab] PASS  free disk space: NN GB
[lab] PASS  internet reachable
[lab] doctor: all checks passed.
```

> **Do not continue to the build until all doctor checks pass.**

Note that `doctor` checks for WSLg but **does not** check Windows interoperability.
That is why section 8 is a separate, mandatory step: `doctor` can pass while
interop is broken, and the failure would only surface during the build.

---

## 12. Build the lab

**Ubuntu / WSL:**

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
guide does not promise an exact time.

Before and during the build:

- **Docker Desktop must be open and show Engine running.** If it shows a Play
  button, press it and wait.
- **Do not let the computer sleep** mid-build.

If the build fails, use the matching troubleshooting section:

- [Docker daemon is unreachable](#docker-daemon-is-unreachable)
- [Docker socket is missing](#docker-socket-is-missing)
- [Docker Compose is unavailable](#docker-compose-is-unavailable)
- [docker-credential-desktop.exe fails](#docker-credential-desktopexe-fails)
- [WSLInterop is missing](#wslinterop-is-missing)

---

## 13. Run Starter checks

**Ubuntu / WSL:**

```bash
./scripts/lab check starter
```

This verifies the Starter environment. It checks that Docker is running, the lab
image is built, the third-party sources manifest is present, the UR5 description
was fetched into `src/external/`, and the workcell and `module_03` launch files
are present.

**Expected output:** every line is `PASS`, ending with:

```
[lab] Environment looks good. Start the cell:
[lab]   ./scripts/lab start module_03
```

> The `starter` check target exists in the free Starter Edition. In the paid
> editions, verify per module instead — for example `./scripts/lab check module_03`.

---

## 14. Launch Module 03

**Ubuntu / WSL:**

```bash
./scripts/lab start module_03
```

This launches the UR5 simulation workcell: Gazebo + MoveIt + RViz.

**Expected output:** two windows appear as normal Windows windows:

- **Gazebo**, showing the UR5 arm, the Robotiq gripper, the simulated depth
  camera, a table/workcell, and the **pallet**.
- **RViz**, with the robot model, TF frames, and the **MotionPlanning** panel.

Graphics may be slower than native Linux (software rendering), but the scene must
be usable.

> If Gazebo or RViz does not appear, see
> [Gazebo or RViz does not appear](#gazebo-or-rviz-does-not-appear).

Leave this running for the next section. When you are done, stop it with `Ctrl+C`
in the terminal that launched it.

---

## 15. Verify MoveIt2 Plan and Execute

With Module 03 running, prove the full pipeline end to end.

In **RViz**:

1. Find the **MotionPlanning** panel.
2. Drag the interactive marker at the end-effector to a new, reachable pose.
3. Click **Plan**. A preview trajectory (a "ghost" arm) appears.
4. Click **Execute**.
5. **The robot moves in Gazebo** to match.

If the arm moves, you have validated the whole stack:

```
Windows 11 → WSL2 → Ubuntu 22.04 → Docker Desktop → ROS2 Humble → MoveIt2 → Gazebo → WSLg
```

Stop the module with `Ctrl+C` in its terminal when you are finished.

---

## 16. Open a second ROS2 terminal

You often want a second terminal to inspect a running simulation. Leave Module 03
running in the first terminal and open a second one.

**Terminal 1 — PowerShell:**

```powershell
wsl -d Ubuntu-22.04
```

**Terminal 1 — Ubuntu / WSL:**

```bash
cd ~/industrial_ros2_manipulation_lab
./scripts/lab start module_03
```

Leave it running. Open a **new** PowerShell window:

**Terminal 2 — PowerShell:**

```powershell
wsl -d Ubuntu-22.04
```

**Terminal 2 — Ubuntu / WSL:**

```bash
cd ~/industrial_ros2_manipulation_lab
./scripts/lab shell
```

What `./scripts/lab shell` does:

- It starts a **separate, temporary lab container** and drops you into a bash
  shell where ROS2 is already sourced.
- That container shares the host network and IPC namespace, so it participates in
  the **same ROS2 graph** as the running simulation — it can see the same topics
  and their data.
- It is **not** the same container that runs Gazebo and RViz; it is a second
  container joining the graph.
- Leave it with `exit`. Because it runs with `--rm`, the temporary container is
  removed when you exit.

**Inside the lab container:**

```bash
ros2 node list
ros2 topic list
ros2 service list
ros2 action list
ros2 topic echo /joint_states
```

You should see the simulation's nodes and topics, and `ros2 topic echo
/joint_states` should stream the robot's joint positions.

You can also run a single command without opening an interactive shell. This
starts the same kind of temporary container, runs the command, and exits:

**Ubuntu / WSL:**

```bash
./scripts/lab exec ros2 node list
```

> If `ros2 topic list` shows the topics but `ros2 topic echo` receives nothing,
> see [Second Terminal Sees the Topics but Receives No Data](docker_troubleshooting.md#second-terminal-sees-the-topics-but-receives-no-data).

---

## 17. Test Starter feature gating

Paid modules are not part of the Starter Edition. They must fail cleanly — a clear
upgrade notice, never a traceback.

**Ubuntu / WSL:**

```bash
for c in module_05 module_06 module_07 module_09; do
  echo "════════ $c"
  ./scripts/lab start "$c" 2>&1 | head -8
done

./scripts/lab start --mode hardware 2>&1 | head -8
```

**Expected output:** clean upgrade notices, for example:

```
[lab] Module 05 (Blind Pick-and-Place) is available in the Simulation Track.
```

There must be **no** Python traceback, **no** "package not found", **no**
"command not found", and no hung process.

---

## Daily startup workflow

Every time you return to the lab:

1. Start **Docker Desktop**. Wait until it shows **Engine running** (press **Play**
   if the engine is stopped).
2. Open **PowerShell** and enter Ubuntu:

**PowerShell:**

```powershell
wsl -d Ubuntu-22.04
```

3. In Ubuntu:

**Ubuntu / WSL:**

```bash
cd ~/industrial_ros2_manipulation_lab
./scripts/lab doctor
./scripts/lab start module_03
```

Notes:

- You do **not** rebuild the image every time. Run `./scripts/lab build` again only
  after you change the environment, or when an update requires it.
- If Docker loses its socket after a WSL shutdown, use
  [Docker socket is missing](#docker-socket-is-missing).
- If `cmd.exe` returns `Exec format error`, use
  [Windows executables return Exec format error](#windows-executables-return-exec-format-error).

---

## Troubleshooting

Work top-down. Most Docker problems come from the engine being stopped or the WSL
integration losing its connection.

### Docker Desktop Engine is stopped

Docker Desktop is installed and WSL integration is enabled, but Docker in Ubuntu
does not work, and Docker Desktop shows a **Play** button with CPU/RAM at zero.

This happens after a Windows reboot, Resource Saver, `wsl --shutdown`,
`wsl --terminate`, or closing/restarting Docker Desktop.

Fix:

1. Open Docker Desktop.
2. Press **Play** if present.
3. Wait for **Engine running**.
4. Only then open Ubuntu.

Verify from **PowerShell:**

```powershell
docker version
wsl -l -v
```

`docker version` must show both `Client:` and `Server:`. When the engine is up,
`docker-desktop` appears as `Running` in `wsl -l -v`.

### Docker daemon is unreachable

`./scripts/lab doctor` reports **Docker daemon not reachable**, or commands say
"Cannot connect to the Docker daemon".

- Confirm Docker Desktop is open and shows **Engine running** (press **Play**).
- Confirm **Settings → Resources → WSL Integration** has **Ubuntu-22.04** enabled.
- Do **not** try to start a daemon inside Ubuntu. There is no Docker Engine to
  start there — Docker comes from Docker Desktop.

### Docker socket is missing

Inside Ubuntu you see:

```
/var/run/docker.sock: no such file or directory
docker compose: unknown command
```

The WSL integration lost its connection to Docker Desktop. Verified recovery:

**Ubuntu / WSL:**

```bash
exit
```

**PowerShell:**

```powershell
wsl --terminate Ubuntu-22.04
```

Then:

1. Open Docker Desktop, press **Play** if needed, wait for **Engine running**.
2. Re-open Ubuntu:

**PowerShell:**

```powershell
wsl -d Ubuntu-22.04
```

**Ubuntu / WSL:**

```bash
ls -l /var/run/docker.sock
docker version
docker compose version
docker run --rm hello-world
```

**Expected:** the socket exists, `docker version` shows Client and Server, Compose
works, and `hello-world` runs.

If it still fails, reset the WSL Integration:

1. Docker Desktop → **Settings → Resources → WSL Integration**.
2. Turn **Ubuntu-22.04 OFF** → **Apply & restart** → wait for **Engine running**.
3. Turn **Ubuntu-22.04 ON** → **Apply & restart** → wait for **Engine running**.
4. In PowerShell: `wsl --terminate Ubuntu-22.04`, then reopen Ubuntu.

> This is not fixed by installing a second Docker daemon inside Ubuntu. Do not do
> that — it creates a conflicting engine.

### Docker Compose is unavailable

`docker compose version` fails, or `docker compose: unknown command`.

- This is almost always the same WSL-integration problem as
  [Docker socket is missing](#docker-socket-is-missing) — follow that recovery.
- Use the space-separated form `docker compose`, not the old `docker-compose`.

### Docker CLI plugins show input/output error

After the integration is lost, plugin lookups can print:

```
docker-compose: input/output error
docker-buildx: input/output error
docker-desktop: input/output error
```

In this state `./scripts/lab doctor` correctly reports the Docker daemon as not
reachable and Compose as unavailable. Recovery is the same as
[Docker socket is missing](#docker-socket-is-missing): exit Ubuntu,
`wsl --terminate Ubuntu-22.04`, bring Docker Desktop back to **Engine running**,
reopen Ubuntu. If it persists, reset the WSL Integration (toggle OFF/ON).

### Windows executables return Exec format error

Interoperability lets Linux run Windows `.exe` files. When it breaks:

**Ubuntu / WSL:**

```bash
cmd.exe /c echo WSL_INTEROP_OK
```

returns `cannot execute binary file: Exec format error`, and

```bash
ls -l /proc/sys/fs/binfmt_misc/WSLInterop
```

shows the file is missing — even though Windows directories are on your `PATH`.

This is the same root cause behind
[docker-credential-desktop.exe fails](#docker-credential-desktopexe-fails), and it
can break the Docker build. Fix it with the `/etc/wsl.conf` recovery below, then
re-verify.

### WSLInterop is missing

`/proc/sys/fs/binfmt_misc/WSLInterop` does not exist. This is a targeted recovery
for this environment — it is **not** a configuration every WSL user needs.

First, back up your current config:

**Ubuntu / WSL:**

```bash
sudo cp /etc/wsl.conf /etc/wsl.conf.backup
cat /etc/wsl.conf
```

If it contains `systemd=true` and no `[interop]` section, edit it. The recovery
configuration used for this lab is:

```ini
[boot]
systemd=false

[interop]
enabled=true
appendWindowsPath=true

[user]
default=<existing-linux-username>
```

**Preserve your own Linux username** in the `[user]` section — use the value
already there, do not invent one.

Why these settings:

- `systemd=false` is a verified recovery for this environment. The lab does not
  require systemd: Docker is provided by Docker Desktop, and ROS2 runs inside
  containers. Do not present this as a general rule for all WSL usage.
- `[interop] enabled=true` restores the ability to run Windows executables, which
  Docker Desktop needs.

Apply it:

**Ubuntu / WSL:**

```bash
exit
```

**PowerShell:**

```powershell
wsl --shutdown
```

Then:

1. Start Docker Desktop, press **Play** if needed, wait for **Engine running**.
2. Reopen Ubuntu:

**PowerShell:**

```powershell
wsl -d Ubuntu-22.04
```

**Ubuntu / WSL:**

```bash
cmd.exe /c echo WSL_INTEROP_OK
ls -l /proc/sys/fs/binfmt_misc/WSLInterop
docker version
docker compose version
docker run --rm hello-world
```

**Do not continue until all of these succeed.**

### docker-credential-desktop.exe fails

The first `./scripts/lab build` fails on `FROM osrf/ros:humble-desktop-full` with:

```
error getting credentials
fork/exec /usr/bin/docker-credential-desktop.exe: exec format error
```

This is **not** a Dockerfile problem, a ROS image problem, a repository problem,
or a Docker Hub authentication problem. It is broken Windows interoperability
inside WSL: Docker Desktop's Windows credential helper cannot be executed.

If `docker run hello-world` and `./scripts/lab doctor` pass but the build fails
with a `.exe` credential helper error, test interop immediately:

**Ubuntu / WSL:**

```bash
cmd.exe /c echo WSL_INTEROP_OK
```

If it returns `Exec format error`, follow
[WSLInterop is missing](#wslinterop-is-missing), then rerun `./scripts/lab build`.

### Gazebo or RViz does not appear

- Re-run the GUI check: `xeyes` (section 4). If `xeyes` fails, WSLg is the problem,
  not the lab — `wsl --update` from PowerShell, `wsl --shutdown`, reboot, retry.
- Inside Ubuntu, confirm WSLg is mounted: `ls /mnt/wslg` should exist, and
  `echo $DISPLAY` is usually `:0`.
- A black/empty Gazebo window on first start can simply be slow software
  rendering — give it 30–60 seconds the first time.
- More detail: [docker_troubleshooting.md](docker_troubleshooting.md).

### Repository was cloned under /mnt/c

`./scripts/lab doctor` reports the repository is on the Windows filesystem, or
builds and file watching misbehave.

Move the clone into the Linux filesystem:

**Ubuntu / WSL:**

```bash
cd ~
git clone https://github.com/LearnRoboticsWROS-Lab/industrial_ros2_manipulation_lab.git
cd industrial_ros2_manipulation_lab
```

Then work from `/home/<linux-user>/industrial_ros2_manipulation_lab`. Do not run
the lab from `/mnt/c/...`.

---

## Final checklist

- [ ] Windows 11
- [ ] WSL2 updated (`wsl --update`)
- [ ] WSLg listed in `wsl --version`
- [ ] Ubuntu-22.04 installed explicitly
- [ ] Ubuntu-22.04 set as default
- [ ] `VERSION_ID="22.04"`
- [ ] `VERSION_CODENAME=jammy`
- [ ] `xeyes` opens
- [ ] Docker Desktop installed
- [ ] WSL2 backend enabled
- [ ] Ubuntu-22.04 WSL Integration enabled
- [ ] Docker Desktop shows **Engine running**
- [ ] `docker version` shows Client and Server
- [ ] `docker compose version` works
- [ ] `docker run --rm hello-world` works without `sudo`
- [ ] `cmd.exe /c echo WSL_INTEROP_OK` works
- [ ] `/proc/sys/fs/binfmt_misc/WSLInterop` exists
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
- [ ] paid commands return clean upgrade notices

When every box is ticked, your Windows 11 environment is validated end to end.
