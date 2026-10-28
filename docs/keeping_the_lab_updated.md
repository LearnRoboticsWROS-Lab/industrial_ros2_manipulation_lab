# Keeping Your Lab Up to Date — TrainIt Is Now Inside ROS2ML

The Industrial ROS2 Manipulation Lab is a **living project**. I keep it updated so your
robotics experience stays current and in step with the tools the industry actually uses.
On **September 17, 2026** I shipped an important update: **TrainIt** is now integrated into
the lab.

## What is TrainIt? (in one minute)

TrainIt is a professional framework for building robot-cell applications without writing all
the plumbing by hand. Its **Setup Assistant** lets you configure a robotic cell — robot,
gripper, scene, motion — and **generates a ready-to-run application bundle**, and its
**Motion Runtime** executes it. Think of it as the fast path from *"I have a cell"* to
*"it runs"* — complementary to the hand-built framework you learn in the paid modules, which
teaches you the architecture underneath.

Good news: **TrainIt (Community) ships in every edition** — Starter, Simulation, and Full —
so you have it whatever tier you're on.

## How to get the update (if you cloned the lab before)

You don't re-clone. Just update the folder where you already cloned the lab:

```bash
cd <the folder where you cloned the lab>   # the one that contains ./scripts/lab
git pull
./scripts/lab build
```

- **`git pull`** fetches the latest lab, including the TrainIt versions it is tested with
  (`trainit.repos`).
- **`./scripts/lab build`** moves TrainIt to those versions and rebuilds **only what's new** — it
  does **not** re-download the whole environment. The Docker image is rebuilt only when the lab's
  Dockerfile changes, and even then Docker reuses everything before the changed step. It takes a
  few minutes.

**Always both.** `git pull` alone does not update TrainIt: TrainIt lives in its own folders
(`src/trainit_*`, each its own git repository), and only `./scripts/lab build` brings them to the
new versions. You can check with `git -C src/trainit_setup_assistant describe --tags`.

**On your computer, not inside the container.** Run both in the lab folder on your machine. The
container keeps nothing: every `./scripts/lab` command starts a fresh one with your lab folder
mounted as `/lab_ws`, so the next `./scripts/lab shell` or `./scripts/lab start` already sees the
update.

If you're cloning the lab **for the first time now**, you already have everything — nothing
extra to do.

After the build you'll also find a **ready-made example generated with TrainIt** in the
workspace (the `yt_ur5_robotiq_*` packages). Run it, study it as a reference, then create your
own bundle.

## October 2026 — TrainIt v8: build the application in the Setup Assistant

The second big TrainIt update. What you get:

- **The Application Composer** (Step 7 of the Setup Assistant). Start from a template (pick and
  place, bin picking, machine tending…), move the robot in RViz and **capture** the waypoints from
  it, then compose the application: PTP / LIN / CIRC moves and blended paths, tasks with repeat,
  retry and "try alternatives", the gripper (open / close, grasp / release), the camera (detect a
  part, grasp it). Every edit is validated as you make it, and the YAML is always the same model.
- **Run it from the Setup Assistant**: generate, build, start the cell, run the application and
  watch the log. The generated application runs in **Gazebo** too, with the gripper and the camera
  (`ros2 launch <your_app> bringup.launch.py mode:=gazebo`).
- **The same motion every cycle**: a PTP to a pose now takes the joint configuration nearest where
  the robot starts — no more a different arm posture from one cycle to the next — and a pose can
  keep the configuration you taught it in.
- **Gazebo cells you generate build and run with `./scripts/lab build`** too (TrainIt 8.2.3), and
  if Gazebo ever refuses to weld a part to the gripper, the log now says so (`ATTACH FAILED ...`)
  instead of the cycle silently going on empty-handed.

The update is fetched exactly as before (`git pull`, then `./scripts/lab build`). Two more TrainIt
packages (`trainit_interfaces`, `trainit_hardware_layer`) now come with it, automatically. The
ready-made `yt_ur5_robotiq_*` example keeps working.

The build now compiles one package at a time, with as many parallel jobs as your free memory allows
(about one per 4 GB), so a big package should not run your computer out of memory. Have plenty of memory and want it
faster? `LAB_BUILD_JOBS=8 ./scripts/lab build`.

**If `git pull` stops with "untracked working tree files would be overwritten by merge" and lists
`src/yt_ur5_robotiq_...` files:** you generated the YouTube example yourself, with the same name as the
copy the lab now ships. Move yours aside and pull again — nothing is lost:

```bash
mkdir -p ~/my_lab_backup
mv src/yt_ur5_robotiq_bundle src/yt_ur5_robotiq_scene_loader_moveit_config ~/my_lab_backup/
git pull
./scripts/lab build
```

**If `git pull` stops with "Your local changes to the following files would be overwritten by
merge":** you edited a file the lab ships. Put your change aside (git keeps it) and pull:

```bash
git stash
git pull
./scripts/lab build
```

`git stash show -p` shows your change; `git stash pop` puts it back on top of the update (if it
touches the same lines the update changed, git marks the file as a conflict for you to resolve).

**If `./scripts/lab build` stops at "importing TrainIt Community" with "Could not checkout ref …
Your local changes … would be overwritten by checkout" for a `src/trainit_…` folder:** you edited
TrainIt's own files. Put your change aside (it stays in that folder's stash) and build again:

```bash
git -C src/<that trainit folder> stash
./scripts/lab build
```

**If a Gazebo cell you generated yourself before this update stops with "executable
'link_attacher_bridge.py' not found on the libexec directory":** generate it again from the Setup
Assistant (Step 8, Generate), or make that one file executable and build again:

```bash
chmod +x src/<your bundle>/<your project>_trainit_config/scripts/link_attacher_bridge.py
./scripts/lab build
```

After the build, `git -C src/trainit_setup_assistant describe --tags` prints `v8.2.3` and
`git -C src/trainit_motion_runtime describe --tags` prints `v2.6.2`.

## Make "pull, then build" a habit

The lab evolves, and TrainIt with it. Before each session, run **`git pull`** and then
**`./scripts/lab build`** in your lab folder to pick up new features and fixes — both, every time.
You won't lose your own work, and the build only recompiles what changed.

Keeping the lab current is **my job** — so that every time you sit down, you're working with an
up-to-date, industry-relevant robotics environment. Thanks for being part of it. 🚀
