#!/usr/bin/env bash
set -euo pipefail

# youtube.sh — run the YouTube demo projects that ship with the Lab.
#
#   ./scripts/lab youtube list             List the available YouTube projects
#   ./scripts/lab youtube run <id>         Launch a project (cell + demo, in Docker)
#
# Projects are ordinary ROS2 packages under src/ named yt_*, each carrying a
# youtube.yaml manifest. This script discovers them from those manifests, so a
# new video is just a new package — no edits here.

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="$REPO_ROOT/docker/compose.yaml"
SRC_DIR="$REPO_ROOT/src"

log() { echo "[lab] $*"; }

# Read a single-line top-level scalar (id/title/package/launch/minimum_edition)
# from a youtube.yaml, trimming whitespace and trailing comments.
field() {
  local file="$1" key="$2"
  grep -E "^${key}:" "$file" 2>/dev/null | head -1 \
    | sed -E "s/^${key}:[[:space:]]*//; s/[[:space:]]*#.*$//; s/[[:space:]]+$//"
}

manifests() { find "$SRC_DIR" -maxdepth 2 -name youtube.yaml 2>/dev/null | sort; }

find_manifest_by_id() {
  local want="$1" f
  while IFS= read -r f; do
    [ -z "$f" ] && continue
    if [ "$(field "$f" id)" = "$want" ]; then echo "$f"; return 0; fi
  done < <(manifests)
  return 1
}

cmd_list() {
  local any=0 f id title edition
  printf '%-22s %-34s %s\n' "ID" "TITLE" "MIN EDITION"
  printf '%-22s %-34s %s\n' "----------------------" "----------------------------------" "-----------"
  while IFS= read -r f; do
    [ -z "$f" ] && continue
    any=1
    id="$(field "$f" id)"; title="$(field "$f" title)"; edition="$(field "$f" minimum_edition)"
    printf '%-22s %-34s %s\n' "${id:-?}" "${title:-?}" "${edition:-starter}"
  done < <(manifests)
  if [ "$any" -eq 0 ]; then
    log "No YouTube projects found (looked for src/*/youtube.yaml)."
  else
    echo
    log "Run one with:  ./scripts/lab youtube run <id>"
  fi
}

cmd_run() {
  local id="${1:-}"
  if [ -z "$id" ]; then
    log "run requires a project id. See: ./scripts/lab youtube list"
    exit 1
  fi
  shift || true
  local launch_args="$*"   # extra 'name:=value' args forwarded to ros2 launch
  local manifest
  if ! manifest="$(find_manifest_by_id "$id")"; then
    log "Unknown project '$id'. Available:"
    cmd_list
    exit 1
  fi

  local pkg launch title
  pkg="$(field "$manifest" package)"
  launch="$(field "$manifest" launch)"
  title="$(field "$manifest" title)"
  if [ -z "$pkg" ] || [ -z "$launch" ]; then
    log "Manifest $manifest is missing 'package' or 'launch'."
    exit 1
  fi

  if ! docker info >/dev/null 2>&1; then
    log "Docker is not reachable. Run ./scripts/lab doctor first."
    exit 1
  fi

  export HOST_UID="$(id -u)"
  export HOST_GID="$(id -g)"

  log "starting YouTube project: ${title:-$id}  ($pkg / $launch $launch_args)"
  log "stop with Ctrl+C"
  docker compose -f "$COMPOSE_FILE" run --rm lab \
    bash -lc "source install/setup.bash 2>/dev/null && ros2 launch $pkg $launch $launch_args" || {
      echo
      log "Project '$id' did not start."
      log "Did you build first?  ./scripts/lab build"
      log "Then check your environment:  ./scripts/lab doctor"
      exit 1
    }
}

SUB="${1:-}"
shift || true
case "$SUB" in
  list) cmd_list ;;
  run)  cmd_run "$@" ;;
  ""|-h|--help|help)
    sed -n '3,10p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
    ;;
  *)
    log "Unknown youtube subcommand: $SUB"
    log "Use: ./scripts/lab youtube list | run <id>"
    exit 1
    ;;
esac
