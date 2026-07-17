#!/usr/bin/env bash
set -euo pipefail

# doctor.sh — verify the student's environment before building or running.
# Every check prints PASS / WARN / FAIL with a fix hint. Exit code is non-zero
# only if at least one FAIL occurred.

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FAILURES=0
WARNINGS=0

pass() { echo "[lab] PASS  $*"; }
warn() { echo "[lab] WARN  $*"; WARNINGS=$((WARNINGS + 1)); }
fail() { echo "[lab] FAIL  $*"; FAILURES=$((FAILURES + 1)); }

echo "[lab] doctor — checking your environment"
echo

# --- Docker -----------------------------------------------------------------
if command -v docker >/dev/null 2>&1; then
  if docker info >/dev/null 2>&1; then
    pass "docker reachable ($(docker --version | sed 's/Docker version //;s/,.*//'))"
  else
    fail "docker installed but the daemon is not reachable.
        Ubuntu: 'sudo systemctl start docker' and make sure you are in the docker group.
        Windows: start Docker Desktop and enable WSL integration."
  fi
else
  fail "docker not found. See docs/windows_wsl2_setup.md or docs/ubuntu_setup.md."
fi

# --- Docker Compose v2 --------------------------------------------------------
if docker compose version >/dev/null 2>&1; then
  pass "docker compose v2 available"
else
  fail "docker compose v2 not available. Install the docker-compose-plugin (Ubuntu) or update Docker Desktop (Windows)."
fi

# --- git ----------------------------------------------------------------------
if command -v git >/dev/null 2>&1; then
  pass "git available"
else
  warn "git not found — you will need it to update the repository."
fi

# --- OS / WSL detection -------------------------------------------------------
IS_WSL=0
if grep -qi microsoft /proc/version 2>/dev/null; then
  IS_WSL=1
  pass "running inside WSL"
else
  pass "running on native Linux"
fi

# --- Repository location (WSL performance trap) --------------------------------
case "$REPO_ROOT" in
  /mnt/c/*|/mnt/d/*|/mnt/e/*)
    fail "repository is under ${REPO_ROOT%%/(*)} (the Windows filesystem).
        Move it into the WSL filesystem for correct performance and permissions:
        cd ~ && git clone https://github.com/LearnRoboticsWROS-Lab/industrial_ros2_manipulation_lab.git"
    ;;
  *)
    pass "repository on a Linux filesystem ($REPO_ROOT)"
    ;;
esac

# --- Display / GUI --------------------------------------------------------------
if [ "$IS_WSL" -eq 1 ]; then
  if [ -d /mnt/wslg ]; then
    pass "WSLg present — GUI applications will display as Windows windows"
  else
    warn "WSLg not found. Update WSL from PowerShell: 'wsl --update', then restart."
  fi
else
  if [ -n "${DISPLAY:-}" ]; then
    pass "DISPLAY is set ($DISPLAY)"
    if command -v xhost >/dev/null 2>&1 && ! xhost 2>/dev/null | grep -q "LOCAL:"; then
      warn "local containers may not open windows yet. Run: xhost +local:"
    fi
  else
    warn "DISPLAY is not set — GUI applications (Gazebo, RViz) will not open.
        Are you on a headless machine or an SSH session without X forwarding?"
  fi
fi

# --- Disk space -----------------------------------------------------------------
AVAILABLE_GB=$(df -BG --output=avail "$REPO_ROOT" 2>/dev/null | tail -1 | tr -dc '0-9' || echo 0)
if [ "${AVAILABLE_GB:-0}" -ge 20 ]; then
  pass "free disk space: ${AVAILABLE_GB} GB"
elif [ "${AVAILABLE_GB:-0}" -ge 10 ]; then
  warn "free disk space: ${AVAILABLE_GB} GB — the image and build need ~15-20 GB; consider freeing space."
else
  fail "free disk space: ${AVAILABLE_GB} GB — not enough. Free at least 20 GB."
fi

# --- Internet --------------------------------------------------------------------
if command -v curl >/dev/null 2>&1 && curl -sI --max-time 8 https://github.com >/dev/null 2>&1; then
  pass "internet reachable"
else
  warn "could not reach github.com — building the image and importing dependencies needs internet."
fi

# --- Summary -----------------------------------------------------------------------
echo
if [ "$FAILURES" -gt 0 ]; then
  echo "[lab] doctor: $FAILURES check(s) FAILED, $WARNINGS warning(s)."
  echo "[lab] Fix the FAIL items above, then run ./scripts/lab doctor again."
  exit 1
fi
if [ "$WARNINGS" -gt 0 ]; then
  echo "[lab] doctor: all critical checks passed ($WARNINGS warning(s) — read them)."
else
  echo "[lab] doctor: all checks passed."
fi
echo "[lab] Next step: ./scripts/lab build"
