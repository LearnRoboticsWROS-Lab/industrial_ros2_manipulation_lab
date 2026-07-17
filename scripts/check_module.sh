#!/usr/bin/env bash
set -euo pipefail

# check_module.sh — STARTER EDITION.
#
# One target: `starter`. It answers the only question a free user has —
# "is my environment actually working?" — and nothing else.
#
# Module checkpoints belong to the paid tracks, and they check application code
# this edition does not ship. Asking for them prints upgrade guidance rather
# than failing on missing files.

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="$REPO_ROOT/docker/compose.yaml"
IMAGE_NAME="industrial-ros2-manipulation-lab:beta"

PASSED=0
FAILED=0

pass() { echo "[lab] PASS  $*"; PASSED=$((PASSED + 1)); }
fail() { echo "[lab] FAIL  $*"; FAILED=$((FAILED + 1)); }
note() { echo "[lab]       $*"; }

TARGET="${1:-starter}"

check_starter() {
  echo "[lab] Starter Edition environment check"
  echo

  if docker info >/dev/null 2>&1; then
    pass "Docker is running"
  else
    fail "Docker is not reachable"
    note "Install Docker, or start the daemon. See docs/docker_troubleshooting.md."
  fi

  if docker image inspect "$IMAGE_NAME" >/dev/null 2>&1; then
    pass "lab image is built ($IMAGE_NAME)"
  else
    fail "lab image not found ($IMAGE_NAME)"
    note "Build it once:  ./scripts/lab build"
  fi

  if [ -f "$REPO_ROOT/.repos/simulation_dependencies.repos" ]; then
    pass "third-party sources manifest present"
  else
    fail ".repos/simulation_dependencies.repos missing"
    note "Without it the UR5 description and Robotiq gripper are never fetched."
  fi

  if [ -d "$REPO_ROOT/src/external/Universal_Robots_ROS2_Description" ]; then
    pass "UR5 description fetched into src/external/"
  else
    fail "UR5 description not fetched yet"
    note "This is normal before the first build. Run:  ./scripts/lab build"
    note "build.sh imports it with 'vcs import' from .repos/simulation_dependencies.repos."
  fi

  if [ -f "$REPO_ROOT/src/lrwros_ur5_workcell/package.xml" ]; then
    pass "workcell package present (lrwros_ur5_workcell)"
  else
    fail "workcell package missing — this clone is incomplete"
  fi

  if [ -f "$REPO_ROOT/src/lrwros_bringup/launch/module_03.launch.py" ]; then
    pass "module_03 launch file present"
  else
    fail "module_03 launch file missing — this clone is incomplete"
  fi

  echo
  echo "[lab] $PASSED passed, $FAILED failed"
  if [ "$FAILED" -eq 0 ]; then
    echo "[lab] Environment looks good. Start the cell:"
    echo "[lab]   ./scripts/lab start module_03"
  else
    echo "[lab] Fix the items above, then re-run:  ./scripts/lab check starter"
    exit 1
  fi
}

case "$TARGET" in
  starter)
    check_starter
    ;;
  module_00)
    echo "[lab] Module 0 is orientation. Its check is the environment check:"
    echo "[lab]   ./scripts/lab check starter"
    ;;
  module_0[1-9]|capstone)
    echo
    echo "[lab] '$TARGET' checkpoints are part of the paid tracks."
    echo "[lab]"
    echo "[lab] They verify application code the Starter Edition does not ship —"
    echo "[lab] so checking them here would be checking something that is not there."
    echo "[lab]"
    echo "[lab] The Starter Edition verifies your environment instead:"
    echo "[lab]   ./scripts/lab check starter"
    echo "[lab]"
    echo "[lab] See UPGRADE.md for the Simulation Track."
    echo
    ;;
  *)
    echo "[lab] Unknown check target: $TARGET"
    echo "[lab] The Starter Edition supports:  ./scripts/lab check starter"
    exit 1
    ;;
esac
