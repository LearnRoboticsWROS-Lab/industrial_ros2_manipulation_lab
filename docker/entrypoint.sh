#!/usr/bin/env bash
set -e

# entrypoint.sh — environment setup for every shell/command in the lab container.
# Kept deliberately tolerant: a stale/foreign overlay or a read-only host runtime
# directory must never stop the container from starting.

# 1. ROS2 Humble
source /opt/ros/humble/setup.bash

# 2. Gazebo Classic
if [ -f /usr/share/gazebo-11/setup.sh ]; then
  source /usr/share/gazebo-11/setup.sh
fi

# 3. Workspace overlay, when built. Tolerate a partial/foreign overlay (e.g. an
#    install/ left over from a native host build shared through the bind mount).
if [ -f /lab_ws/install/setup.bash ]; then
  source /lab_ws/install/setup.bash 2>/dev/null || true
fi

# 4. Gazebo model/resource paths: register every model shipped by packages in
#    the workspace (anything with a model.config), so worlds find their models.
if [ -d /lab_ws/src ]; then
  MODEL_DIRS=$(find /lab_ws/src /lab_ws/install -name model.config -printf '%h\n' 2>/dev/null \
    | xargs -r dirname | sort -u | tr '\n' ':')
  if [ -n "$MODEL_DIRS" ]; then
    export GAZEBO_MODEL_PATH="${MODEL_DIRS}${GAZEBO_MODEL_PATH:-}"
  fi
  export GAZEBO_RESOURCE_PATH="/lab_ws/src:${GAZEBO_RESOURCE_PATH:-}"
fi

# 5. Runtime dir (Qt/Gazebo complain without it). The host value inherited on a
#    Linux desktop (e.g. /run/user/1000) is NOT writable inside the container, so
#    always use a container-local path we can create. GUI still works because
#    RViz/Gazebo use X11 (DISPLAY + /tmp/.X11-unix), not this directory.
export XDG_RUNTIME_DIR="/tmp/runtime-$(id -u)"
mkdir -p "$XDG_RUNTIME_DIR" 2>/dev/null || true
chmod 700 "$XDG_RUNTIME_DIR" 2>/dev/null || true

# 5. Headless rendering.
#    Gazebo Classic renders its camera sensors through OpenGL, and OpenGL needs an X
#    server. With no DISPLAY there is no X server, so gzserver quietly creates no camera
#    at all: /camera/points never appears, and the whole vision module (Module 6) sits
#    there waiting for a point cloud that is never coming. Nothing errors. It just does
#    not work.
#
#    Xvfb is an X server that draws into memory instead of onto a screen. Start one, point
#    DISPLAY at it, and the cell runs — camera and all — on a machine with no GUI: a CI
#    runner, a server, a WSL box without an X forward.
if [ -z "${DISPLAY:-}" ] && command -v Xvfb >/dev/null 2>&1; then
  Xvfb :99 -screen 0 1280x1024x24 >/dev/null 2>&1 &
  export DISPLAY=:99
  export LIBGL_ALWAYS_SOFTWARE=1
  sleep 1
  echo "[lab] no DISPLAY: started a virtual framebuffer on :99 (headless mode)."
  echo "[lab] Gazebo and RViz windows will not appear, but the camera works."
fi

exec "$@"
