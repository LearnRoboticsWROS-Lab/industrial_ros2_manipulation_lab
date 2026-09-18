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

- **`git pull`** fetches the latest lab, including the TrainIt recipe.
- **`./scripts/lab build`** pulls in TrainIt and rebuilds **only what's new** — it does **not**
  re-download the whole environment. The big Docker image stays cached; you'll only see a small
  dependency layer plus TrainIt itself. It takes a couple of minutes.

If you're cloning the lab **for the first time now**, you already have everything — nothing
extra to do.

After the build you'll also find a **ready-made example generated with TrainIt** in the
workspace (the `yt_ur5_robotiq_*` packages). Run it, study it as a reference, then create your
own bundle.

## Make `git pull` a habit

The lab evolves. Before each session, it's good practice to run a quick **`git pull`** (and
**`./scripts/lab build`** if anything changed) in your lab folder to pick up new features and
fixes. You won't lose your own work, and the build stays incremental.

Keeping the lab current is **my job** — so that every time you sit down, you're working with an
up-to-date, industry-relevant robotics environment. Thanks for being part of it. 🚀
