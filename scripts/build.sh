#!/usr/bin/env bash
set -euo pipefail

# build.sh — build the Docker image, import third-party dependencies, and build
# the ROS2 workspace inside the container.

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="$REPO_ROOT/docker/compose.yaml"

log() { echo "[lab] $*"; }

if ! docker info >/dev/null 2>&1; then
  log "Docker is not reachable. Run ./scripts/lab doctor first."
  exit 1
fi

# --- 1. Build the image --------------------------------------------------------
log "building the Docker image (first run downloads a multi-GB base image — be patient)"
export HOST_UID="$(id -u)"
export HOST_GID="$(id -g)"
docker compose -f "$COMPOSE_FILE" build

# --- 2. Import third-party sources via vcs ---------------------------------------
REPOS_FILE="$REPO_ROOT/.repos/simulation_dependencies.repos"
if [ -f "$REPOS_FILE" ]; then
  log "importing third-party dependencies (vcs import from .repos/simulation_dependencies.repos)"
  mkdir -p "$REPO_ROOT/src/external"
  docker compose -f "$COMPOSE_FILE" run --rm lab \
    bash -lc "vcs import --recursive src/external < .repos/simulation_dependencies.repos"
else
  log "NOTE: $REPOS_FILE not found — skipping dependency import."
  log "Third-party packages (UR description, Robotiq, LinkAttacher) will be missing until it exists."
fi

# --- 3. Build the workspace -------------------------------------------------------
log "building the ROS2 workspace (colcon build inside the container)"
docker compose -f "$COMPOSE_FILE" run --rm lab \
  bash -lc "colcon build --symlink-install --base-paths src --packages-skip robotiq_driver robotiq_hardware_tests || { echo; echo '[lab] Workspace build failed. This is expected while the beta src/ packages are being populated.'; echo '[lab] See course/BETA_RELEASE_NOTES.md for current build status.'; exit 1; }"

log "build complete."
log "Next step: ./scripts/lab start demo"
