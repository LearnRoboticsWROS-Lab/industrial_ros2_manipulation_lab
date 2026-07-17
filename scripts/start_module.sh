#!/usr/bin/env bash
set -euo pipefail

# start_module.sh — STARTER EDITION.
#
# The Starter Edition ships one runnable target: the UR5 simulation workcell.
#   start_module.sh module_03      -> the workcell (Gazebo + MoveIt + RViz)
#   start_module.sh demo           -> the same cell, as the Module 0 demo
#
# Every other module is part of a paid track. Those targets do not fail here —
# they explain what they are and where to get them. A free user should never see
# a Python traceback or a "package not found" for something we chose not to ship.

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="$REPO_ROOT/docker/compose.yaml"

log() { echo "[lab] $*"; }

TARGET="${1:-}"
if [ -z "$TARGET" ]; then
  log "No target given."
  log "The Starter Edition runs the simulation workcell:"
  log "  ./scripts/lab start module_03"
  exit 1
fi

upgrade_notice() {
  # $1 = what the user asked for, $2 = one line on what it actually is
  echo
  log "$1 is available in the Simulation Track."
  log ""
  log "  What it is:  $2"
  log ""
  log "The Starter Edition includes the Docker environment and the runnable UR5"
  log "simulation workcell. It is a complete, working cell — but it is not the"
  log "course: the application layer on top of it is the paid track."
  log ""
  log "Upgrade to the Simulation Track to build the full pick-and-place"
  log "application (blind, then vision-guided, then Behavior Trees, then your"
  log "own capstone)."
  log ""
  log "  See UPGRADE.md"
  log ""
  log "What you can run right now:"
  log "  ./scripts/lab start module_03      the UR5 + Robotiq + camera workcell"
  log "  ./scripts/lab check starter        verify your setup"
  echo
  exit 0
}

run_launch() {
  local launch_file="$1"
  local description="$2"

  if ! docker info >/dev/null 2>&1; then
    log "Docker is not reachable. Run ./scripts/lab doctor first."
    exit 1
  fi

  export HOST_UID="$(id -u)"
  export HOST_GID="$(id -g)"

  log "starting: $description"
  log "stop with Ctrl+C"
  docker compose -f "$COMPOSE_FILE" run --rm lab \
    bash -lc "source install/setup.bash 2>/dev/null && ros2 launch lrwros_bringup $launch_file" || {
      echo
      log "This target did not start."
      log "Expected next step: $description."
      log ""
      log "Most common causes, in order:"
      log "  1. The workspace was never built:   ./scripts/lab build"
      log "  2. Docker is not healthy:           ./scripts/lab doctor"
      log "  3. Third-party sources missing — build.sh fetches the UR5"
      log "     description, the Robotiq gripper and IFRA_LinkAttacher via"
      log "     'vcs import' from .repos/simulation_dependencies.repos."
      log ""
      log "See STARTER_GUIDE.md and docs/docker_troubleshooting.md."
      exit 1
    }
}

case "$TARGET" in
  demo)
    run_launch "demo.launch.py" "launch the demo cell (UR5 + Robotiq + camera)"
    ;;
  module_03)
    run_launch "module_03.launch.py" "launch the UR5 simulation workcell (Gazebo + MoveIt + RViz)"
    ;;

  # ---- documentation-only modules -------------------------------------------
  module_00)
    log "Module 0 is orientation: install Docker, run the cell, understand the layout."
    log "It has no launch target. Start here:"
    log "  ./scripts/lab doctor"
    log "  ./scripts/lab build"
    log "  ./scripts/lab start module_03"
    log ""
    log "The guided Module 0 lessons are free on Teachable — see UPGRADE.md."
    ;;
  module_01)
    upgrade_notice "Module 01 (ROS2 Foundations)" \
      "nodes, topics, services, parameters and launch files, taught on this cell."
    ;;
  module_02)
    upgrade_notice "Module 02 (Docker Workflow)" \
      "how the image is built, and how to work inside it without fighting it."
    ;;

  # ---- paid application layer -----------------------------------------------
  module_04)
    upgrade_notice "Module 04 (ros2_control and MoveIt2)" \
      "controllers, planning groups and the motion stack driving this cell."
    ;;
  module_05)
    upgrade_notice "Module 05 (Blind Pick-and-Place)" \
      "your first complete application: pick and place from fixed poses."
    ;;
  module_06)
    upgrade_notice "Module 06 (Vision-Guided Pick-and-Place)" \
      "a depth camera finds the object; the robot picks what it sees."
    ;;
  module_07)
    upgrade_notice "Module 07 (Behavior Tree Architecture)" \
      "the same task rebuilt on a robot-agnostic Behavior Tree framework."
    ;;
  module_08)
    upgrade_notice "Module 08 (Capstone)" \
      "you design and build your own application, and put it in your portfolio."
    ;;

  # ---- Full Track ------------------------------------------------------------
  module_09)
    echo
    log "Module 09 (Simulation to Reality) is part of the Full Track."
    log ""
    log "  What it is:  the same architecture deployed on a real industrial cell —"
    log "               a Fairino FR3WML cobot, a RealSense camera, a Jetson Orin"
    log "               Nano running YOLO and 6D pose estimation."
    log ""
    log "It is designed to be studied WITHOUT owning any hardware."
    log ""
    log "The Starter Edition is simulation only. See UPGRADE.md for both tracks."
    echo
    ;;

  mode_mock|mode_sim)
    upgrade_notice "This run mode" \
      "mock and sim modes drive the application layer, which is the paid track."
    ;;

  mode_hardware)
    echo
    log "Hardware mode is a deployment case study, not a simulation mode."
    log ""
    log "It requires a real robot cell: a Fairino FR3WML, a gripper, a RealSense"
    log "camera and a Jetson. It is never required to learn this material, and it"
    log "is not part of the Starter Edition."
    log ""
    log "No real hardware is required for the main simulation path — which is"
    log "exactly what the Starter Edition gives you:"
    log "  ./scripts/lab start module_03"
    log ""
    log "The deployment case study is Module 9, in the Full Track. See UPGRADE.md."
    echo
    ;;

  *)
    log "Unknown target: $TARGET"
    log ""
    log "The Starter Edition runs:"
    log "  ./scripts/lab start module_03      the UR5 simulation workcell"
    log "  ./scripts/lab start demo           the same cell as the Module 0 demo"
    log ""
    log "Other modules are part of the paid tracks — see UPGRADE.md."
    exit 1
    ;;
esac
