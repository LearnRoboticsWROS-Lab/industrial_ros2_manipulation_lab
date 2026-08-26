# How to add a YouTube project

The fastest path is to copy the reference project and trim it to your task.

```bash
cp -r src/yt_vision_pick_place src/yt_<your_id>
```

Then work through this checklist.

## 1. Rename the package

- `package.xml`: set `<name>yt_<your_id></name>` and the description.
- `CMakeLists.txt`: set `project(yt_<your_id>)`.
- Remove nodes/launch/config you don't need.

## 2. Write the manifest — `src/yt_<your_id>/youtube.yaml`

Keep `id`, `title`, `package`, `launch`, `minimum_edition` on single lines
(the CLI parses them without a YAML tool).

```yaml
id: <your_id>
title: <Human Title>
package: yt_<your_id>
launch: <your>.launch.py
minimum_edition: starter        # the lowest edition this must run on
youtube_url: null

runtime:
  simulation: true
  real_robot: false

requires: []                    # cell capabilities you rely on
learning_outcomes: []
scope: []                       # what the demo DOES
not_in_scope: []                # what belongs to the paid tracks
```

## 3. Stay inside the edition boundary

Depend only on what `minimum_edition` ships. For `starter` that means the cell
(`lrwros_ur5_workcell`, `lrwros_ur5_moveit_config`), the controllers, the
camera, MoveIt2, and the LinkAttacher — **not** `industrial_bt_framework`,
`lrwros_ur5_ik`, `lrwros_3d_cv`, the BT packages, or any hardware bridge.

Verify before you commit:

```bash
python3 tools/edition_export/youtube_boundary_check.py
```

## 4. Reuse the cell, don't rebuild it

Include the cell's launch (as `vision_pick_place.launch.py` does) instead of
copying robot descriptions, MoveIt configs or worlds. Add only the nodes that
make your task work.

## 5. Keep the scope honest

A YouTube project solves one task and stops. Clean, parameterised, readable
code — but no reusable-skill framework, no Behavior Trees, no recovery engine.
Put those in the project README under "What this deliberately does NOT do" and
point to the paid tracks. That contrast is the point.

## 6. Register it for humans

Add a row to [../README.md](../README.md)'s "Available projects" table.
`./scripts/lab youtube list` will pick it up automatically from the manifest.

## 7. Ship it in every edition

The export manifests list YouTube packages explicitly. Add
`- path: src/yt_<your_id>` to all three:
`tools/edition_export/{starter,simulation,full}_manifest.yaml`.
The same project ships identically to Starter, Simulation and Full.
