# Docker Environment

ROS2 Humble + Gazebo Classic + MoveIt2 + ros2_control in one image; the
repository is bind-mounted at `/lab_ws` as the colcon workspace. **No native
ROS2 installation is required.**

## Files

| File | Role |
|---|---|
| `Dockerfile` | The lab image: `osrf/ros:humble-desktop-full` + control/planning/perception packages + a non-root user matching your UID/GID |
| `compose.yaml` | The `lab` service: host networking, GUI mounts (X11 + WSLg), repo bind mount |
| `entrypoint.sh` | Sources ROS + Gazebo + the workspace overlay; builds `GAZEBO_MODEL_PATH` from every `model.config` in the workspace |

## Normal usage

You rarely touch these files directly — the `lab` CLI wraps them:

```bash
./scripts/lab build          # compose build + vcs import + colcon build
./scripts/lab start demo     # compose run lab ... ros2 launch
```

Manual equivalents, if you want them:

```bash
export HOST_UID=$(id -u) HOST_GID=$(id -g)
docker compose -f docker/compose.yaml build
docker compose -f docker/compose.yaml run --rm lab bash        # a shell inside
```

## Design decisions (worth reading once — Module 2 explains them)

- **Sources are not baked into the image.** The repo is a bind mount; you edit on the host, build in the container, and never rebuild the image for code changes.
- **Non-root user with your UID/GID** (build args) so files created inside the container belong to you on the host.
- **Host networking** keeps ROS2 DDS discovery trivial and matches how multi-machine setups (PC + Jetson, Module 9) work.
- **GUI:** WSLg mounts for Windows 11; X11 socket for Ubuntu (`xhost +local:` once per session).
- **Third-party sources** come from `.repos/` via `vcs import` into `src/external/` (git-ignored) — the image stays generic, pins live in versioned text files.

## Troubleshooting

See [../docs/docker_troubleshooting.md](../docs/docker_troubleshooting.md).
