#!/usr/bin/env bash
set -euo pipefail

# start_demo.sh — launch the Module 0 demo: the UR5 + Robotiq + depth camera
# workcell in Gazebo with the MoveIt planning scene in RViz.

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="$REPO_ROOT/docker/compose.yaml"
# Must match the image name in docker/compose.yaml.
IMAGE_NAME="industrial-ros2-manipulation-lab:beta"

log() { echo "[lab] $*"; }

if ! docker info >/dev/null 2>&1; then
  log "Docker is not reachable. Run ./scripts/lab doctor first."
  exit 1
fi

# Reliable image check: 'docker compose images' only lists images that have a
# container, and the build uses ephemeral --rm containers, so inspect the image
# by name instead.
if ! docker image inspect "$IMAGE_NAME" >/dev/null 2>&1; then
  log "The lab image is not built yet. Run: ./scripts/lab build"
  exit 1
fi

# Allow local containers to use the X server on native Linux (no-op elsewhere).
if command -v xhost >/dev/null 2>&1 && [ -n "${DISPLAY:-}" ] && ! grep -qi microsoft /proc/version 2>/dev/null; then
  xhost +local: >/dev/null 2>&1 || true
fi

log "starting the UR5 workcell demo (Gazebo + MoveIt + RViz)"
log "first start can take 30-60 s; stop with Ctrl+C"

export HOST_UID="$(id -u)"
export HOST_GID="$(id -g)"

if ! docker compose -f "$COMPOSE_FILE" run --rm lab \
  bash -lc "test -f install/setup.bash"; then
  log "The workspace is not built yet inside the container."
  log "Expected next step: ./scripts/lab build"
  log "See docs/STUDENT_STEP_BY_STEP_GUIDE.md, section 6."
  exit 1
fi

docker compose -f "$COMPOSE_FILE" run --rm lab \
  bash -lc "source install/setup.bash && ros2 launch lrwros_bringup demo.launch.py" || {
    echo
    log "The demo did not start."
    log "If the error above says the package or launch file was not found, this beta"
    log "build has not populated src/lrwros_bringup yet."
    log "Expected next step: launch the UR5 simulation workcell."
    log "See docs/STUDENT_STEP_BY_STEP_GUIDE.md for the manual procedure and"
    log "course/BETA_RELEASE_NOTES.md for what is implemented in this beta."
    exit 1
  }
