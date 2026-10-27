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

# --- 2b. Import TrainIt Community (pinned to a release tag) -----------------------
# TrainIt (TSA/TMR/TP) is the manipulation framework the course teaches. It is
# fetched from GitHub at the tags trainit.repos pins into src/trainit_* (not copied from disk), so a fresh
# clone — including the free Starter edition — gets TrainIt and can run it here.
TRAINIT_REPOS_FILE="$REPO_ROOT/trainit.repos"
if [ -f "$TRAINIT_REPOS_FILE" ]; then
  log "importing TrainIt Community (vcs import from trainit.repos, at its pinned release tags)"
  docker compose -f "$COMPOSE_FILE" run --rm lab \
    bash -lc "vcs import src < trainit.repos"
else
  log "NOTE: $TRAINIT_REPOS_FILE not found — skipping TrainIt import (TSA/TMR/TP will be missing)."
fi

# --- 3. Build the workspace -------------------------------------------------------
# Memory-safe parallelism. One C++ compile of a MoveIt-based package (TrainIt's motion runtime above
# all) can take several GB; colcon's default -- many packages at once, each with `make -j<all cores>` --
# has run machines out of memory and frozen them. So: one package at a time, LAB_BUILD_JOBS compile jobs
# inside it (default: 1 per 4 GB of available memory, at least 1, at most the cores). Set LAB_BUILD_JOBS
# yourself to change it (e.g. LAB_BUILD_JOBS=8 ./scripts/lab build on a machine with the memory for it).
if [ -z "${LAB_BUILD_JOBS:-}" ]; then
  avail_gb=$(awk '/MemAvailable/ {print int($2 / 1048576)}' /proc/meminfo 2>/dev/null || echo 4)
  LAB_BUILD_JOBS=$(( avail_gb / 4 ))
  [ "$LAB_BUILD_JOBS" -lt 1 ] && LAB_BUILD_JOBS=1
  cores=$(nproc 2>/dev/null || echo 2)
  [ "$LAB_BUILD_JOBS" -gt "$cores" ] && LAB_BUILD_JOBS=$cores
fi
log "building the ROS2 workspace (colcon build inside the container: one package at a time, ${LAB_BUILD_JOBS} compile jobs; LAB_BUILD_JOBS changes it)"
docker compose -f "$COMPOSE_FILE" run --rm -e MAKEFLAGS="-j${LAB_BUILD_JOBS}" -e CMAKE_BUILD_PARALLEL_LEVEL="${LAB_BUILD_JOBS}" lab \
  bash -lc "colcon build --symlink-install --parallel-workers 1 --base-paths src --packages-skip robotiq_driver robotiq_hardware_tests || { echo; echo '[lab] Workspace build failed. This is expected while the beta src/ packages are being populated.'; echo '[lab] See course/BETA_RELEASE_NOTES.md for current build status.'; exit 1; }"

log "build complete."
log "Next step: ./scripts/lab start demo"
