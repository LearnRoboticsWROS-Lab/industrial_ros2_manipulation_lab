# Docker Troubleshooting

Work top-down: most problems are caught by `./scripts/lab doctor`. Every fix below
is safe to re-run.

## First Response to Any Problem

```bash
./scripts/lab doctor
```

Read the FAIL/WARN lines. They cover: Docker not reachable, compose missing,
display not set, repo under `/mnt/c`, low disk, no internet.

## GUI Problems (Gazebo/RViz window does not appear)

**Ubuntu (X11):**
```bash
xhost +local:          # allow local containers to open windows
echo $DISPLAY          # should print something like :0 or :1
```
On Wayland sessions, XWayland usually handles it; if windows stay blank, log in
with "Ubuntu on Xorg" and retry.

**Windows 11 (WSLg):**
```bash
ls /mnt/wslg           # should exist inside the WSL terminal
echo $DISPLAY          # usually :0
```
If missing: update WSL (`wsl --update` from PowerShell), restart Docker Desktop,
reopen the Ubuntu terminal.

**Both:** black/empty Gazebo window on first start can simply be slow software
rendering — give it 30–60 s the first time.

## "Cannot connect to the Docker daemon"

- Ubuntu: `sudo systemctl start docker`, and make sure your user is in the docker group (`groups | grep docker`; if not: `sudo usermod -aG docker $USER`, then log out/in).
- Windows: start Docker Desktop and wait until it reports "Engine running" (press **Play** if the engine is stopped); check WSL integration is enabled for Ubuntu-22.04.

**Windows only — deeper Docker Desktop / WSL problems** (missing socket, CLI
plugins showing `input/output error`, a build failing on
`docker-credential-desktop.exe: exec format error`, or `cmd.exe` returning
`Exec format error`) are covered in
[windows_wsl2_setup.md → Troubleshooting](windows_wsl2_setup.md#troubleshooting).

## Permission Errors on Files Created by the Container

The image builds with a user matching your UID/GID. If you see root-owned files
(usually after running docker manually):

```bash
sudo chown -R $USER:$USER .
./scripts/lab build     # rebuild uses your UID/GID build args
```

## Slow Builds or File Watching Broken (Windows)

Your clone is probably under `/mnt/c/...`. Move it inside WSL:

```bash
cd ~ && git clone https://github.com/LearnRoboticsWROS-Lab/industrial_ros2_manipulation_lab.git && cd industrial_ros2_manipulation_lab
```

## Volume / Persistence Confusion

The repository folder is bind-mounted into the container at `/lab_ws`. Everything
you edit on the host is instantly visible inside, and vice versa. `build/`,
`install/`, `log/` live in the repo folder too (git-ignored) — deleting them and
re-running `./scripts/lab build` is always safe.

## Rebuilding From Scratch

```bash
docker compose -f docker/compose.yaml down --remove-orphans
rm -rf build/ install/ log/
./scripts/lab build
```

Nuclear option (also removes the image and build cache):

```bash
docker system prune -a     # WARNING: removes ALL unused Docker images on your machine
./scripts/lab build
```

## "Package not found" After a Successful Build

You are probably in a shell that has not sourced the overlay:

```bash
source install/setup.bash      # inside the container, from /lab_ws
```

The provided entrypoint does this automatically for new shells.

## Second Terminal Sees the Topics but Receives No Data

Symptom: `./scripts/lab exec ros2 topic list` shows a running simulation's
topics (`/tf`, `/joint_states`, …), but `ros2 topic echo <topic>` or
`ros2 run tf2_tools view_frames` receives nothing (empty output / empty TF).

Cause: ROS2 (FastDDS) discovers topics across separate containers over the
network, but its default same-host transport is **shared memory** (`/dev/shm`),
which separate containers do not share. So discovery works, data does not.

Fix (already in this repo): `docker/compose.yaml` sets `ipc: host`, which shares
`/dev/shm` across the lab containers. If you edited compose and hit this, make
sure `ipc: host` is present. Also: containers started **before** adding it do not
benefit — restart the simulation (`Ctrl+C`, then `./scripts/lab start ...`) so
the new container picks up the setting.

## Still Stuck?

Open an issue with: your OS, `./scripts/lab doctor` output, the exact command you
ran, and the full error text.
