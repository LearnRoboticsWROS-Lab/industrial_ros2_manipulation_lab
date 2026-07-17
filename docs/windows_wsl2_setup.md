# Windows 11 Setup — WSL2, Docker Desktop, VS Code

Goal: run the whole lab on a Windows 11 laptop. ROS2 runs inside Docker inside
WSL2; GUI applications (Gazebo, RViz) display through WSLg. **No native ROS2
installation is required.**

## 1. Enable WSL2 and Install Ubuntu 22.04

Open PowerShell **as Administrator**:

```powershell
wsl --install -d Ubuntu-22.04
```

Reboot if asked, then create your Linux username/password when Ubuntu starts.
Verify:

```powershell
wsl --version        # WSL version 2.x, WSLg listed
wsl -l -v            # Ubuntu-22.04, VERSION 2
```

If Ubuntu shows VERSION 1: `wsl --set-version Ubuntu-22.04 2`.

## 2. Install Docker Desktop

1. Download Docker Desktop for Windows and install it.
2. In Docker Desktop → *Settings* → *General*: enable **Use the WSL 2 based engine**.
3. *Settings* → *Resources* → *WSL integration*: enable integration with **Ubuntu-22.04**.
4. In an Ubuntu (WSL) terminal, verify:

```bash
docker --version
docker compose version
docker run --rm hello-world
```

## 3. Install VS Code

1. Install VS Code **on Windows** (not inside WSL).
2. Install extensions: **WSL** and **Dev Containers**.
3. From an Ubuntu terminal, `code .` opens VS Code connected to WSL.

## 4. Clone the Repository — IN THE WSL FILESYSTEM

This is the single most common Windows mistake. Clone **inside Linux**, never
under `/mnt/c/...`:

```bash
# CORRECT (inside the Ubuntu/WSL terminal):
cd ~
git clone https://github.com/LearnRoboticsWROS/industrial_ros2_manipulation_lab.git
cd industrial_ros2_manipulation_lab

# WRONG — do not do this:
# cd /mnt/c/Users/you/Documents && git clone ...
```

Why: files under `/mnt/c` cross a filesystem bridge that makes colcon builds ~10x
slower and breaks file permissions and file-watching.

## 5. Verify Everything

```bash
./scripts/lab doctor
```

`doctor` checks: Docker reachable, compose available, display/WSLg present, repo
location (warns if under `/mnt/c`), disk space, internet.

## 6. GUI Notes (WSLg)

Windows 11 ships WSLg, so Gazebo and RViz windows appear like normal Windows
windows — no X server to install. The compose file already mounts the WSLg
sockets. If a GUI does not appear, see
[docker_troubleshooting.md](docker_troubleshooting.md).

## 7. Recommended Workflow

- Open the repo with VS Code → *Dev Containers: Reopen in Container* (uses `.devcontainer/`).
- Or stay terminal-based: `./scripts/lab build`, `./scripts/lab start demo`.

## Known Windows-Specific Limits

- First `lab build` downloads a multi-GB image: expect several minutes on a normal connection.
- Gazebo runs with software rendering unless GPU passthrough is configured; the workcell is sized to stay usable anyway.
- Keep Docker Desktop running while you work; if WSL is shut down, restart Docker Desktop first.
