# CLAUDE.md

Working agreement for AI agents and contributors in this repository.
Read [SPEC.md](SPEC.md) before changing anything that crosses a node boundary.

---

## Project in one paragraph

DRISHTI-UGV is a ROS 2 Jazzy software module that drives an outdoor unmanned
ground vehicle from Point A to Point B using cameras as the primary sensor,
with no GPS. Mature open source carries the infrastructure (RTAB-Map for
visual SLAM, `elevation_mapping_cupy` for terrain, Nav2 for planning and
control); our own code is the camera-to-traversability fusion layer, a
deterministic safety supervisor, and the evaluation harness. Development is
simulation-first in NVIDIA Isaac Sim. Built for SIH 2026 Problem Statement
26126 (Bharat Electronics Limited).

---

## Current state — read this first

**Phase 0, partially blocked.** `ugv_ws/` now exists with two packages —
`drishti_msgs` and `drishti_bringup` — but **it has never been built.** No
machine on the project has ROS 2 installed. The manifests, message definitions
and params file are syntax-checked only.

The blocker is hardware: the development machine has no NVIDIA GPU, so neither
Isaac Sim nor `elevation_mapping_cupy` can run on it at all. See
[STATUS.md](STATUS.md) **B3** — read it before planning any work that assumes a
GPU.

Consequences:

- **Do not invent build or test commands, and do not report `colcon build` as
  working.** It is unverified. If you are asked to run something that cannot
  run here, say so rather than simulating a result.
- Treat the first successful `colcon build` as the real Phase 0 acceptance
  event, and fill *Pinned versions* in STATUS.md when it happens.
- Nothing below `drishti_msgs` and `drishti_bringup` exists yet. The remaining
  packages in the layout are planned, not present.

---

## Non-negotiables

These are design invariants. Do not "improve" past them without an explicit
decision recorded in [STATUS.md](STATUS.md).

1. **The safety supervisor is deterministic and owns `/cmd_vel`.**
   It contains no learned components. Nav2 publishes to `/cmd_vel_nav`; the
   supervisor is the only publisher on `/cmd_vel`. If a change lets Nav2 reach
   the base directly, that change is wrong.

2. **Loss of input is a stop condition.** Stale camera, stale depth, lost pose
   or an invalid command means STOP. Never treat missing data as "probably
   fine".

3. **Unknown terrain is expensive, never free.** Unobserved, low-visibility or
   low-confidence cells get high cost so the planner routes around ignorance.

4. **One SLAM system in the runtime graph.** RTAB-Map. ORB-SLAM3 is an offline
   benchmark only and is GPLv3 — it never enters the shipped build.

5. **No GPS/GNSS anywhere in the runtime graph**, including initialisation.

6. **Nothing publishes a TF edge it does not own.** Two publishers on one edge
   is the most expensive bug available here.

7. **`use_sim_time` is `true` for every node** when running against the
   simulator. One node on the wrong clock corrupts the map.

8. **Phase gates hold.** Phase N+1 does not begin until Phase N ships a
   runnable artefact. A sophisticated model must never be used to paper over a
   broken TF tree, odometry or navigation foundation.

9. **No GPLv3 code in the shipped build.** Check
   [REFERENCES.md](REFERENCES.md) §3 before adding a dependency.

10. **We do not claim "100% accuracy".** Claims are mission-level metrics with
    a measurement method. See [EVALUATION.md](EVALUATION.md).

---

## Repository layout

```
drishti-ugv/
├── README.md            entry point
├── PRD.md               requirements, success criteria, risks
├── SPEC.md              architecture, interfaces, algorithms   ← the contract
├── SETUP.md             machine requirements and install order
├── TASK.md              phased backlog with acceptance criteria
├── EVALUATION.md        metrics and the test scenario catalog
├── REFERENCES.md        upstream repos, licences, documentation
├── STATUS.md            living state and decision log
├── CLAUDE.md            this file
└── ugv_ws/              ROS 2 colcon workspace
    └── src/
        ├── drishti_msgs/        SafetyState, PerceptionHealth      ← exists
        └── drishti_bringup/     shared params, launch              ← exists
```

Planned, not yet present:

```
    └── src/
        ├── drishti_perception/      detection, segmentation, health
        ├── drishti_traversability/  elevation → cost fusion, Nav2 layer
        ├── drishti_safety/          deterministic supervisor
        └── drishti_eval/            metrics, scenario runner, reports
├── sim/                 simulator scenes, robot description, randomisation
└── docker/              reproducible environment
```

Note the workspace lives at `drishti-ugv/ugv_ws/`, not at the repository root —
the repository root also carries `deck/` and `source/`. Shared parameters live
in `drishti_bringup/config/`, not a top-level `config/`.

---

## Commands

> **Status: planned.** None of these work until Phase 0 creates the workspace.
> Do not cite them as if they run today.

```bash
# build
colcon build --symlink-install

# source
source install/setup.bash

# test
colcon test --event-handlers console_direct+
colcon test-result --verbose

# lint (ament, per package)
colcon test --packages-select <pkg> --ctest-args -R lint
```

Launch entry points are defined in `drishti_bringup` and will be listed here
once they exist.

---

## Conventions

### Language split

- **Python** — perception nodes, tooling, evaluation, scenario generation.
- **C++** — real-time nodes, the Nav2 costmap layer, the safety supervisor.

The supervisor is C++ because its latency budget is < 200 ms end to end and it
must be trivially auditable.

### Naming

- Packages: `drishti_<area>`, snake_case.
- Nodes: snake_case, named for what they do (`traversability_fusion`), not for
  how (`gpu_node`).
- Topics: as specified in [SPEC.md](SPEC.md) §4. **Adding or renaming a topic
  is a spec change — update SPEC.md in the same commit.**
- Frames: as specified in SPEC.md §3.1. Optical frames end in `_optical`.

### Parameters

- No magic numbers in source. Every threshold, weight and rate lives in a
  params YAML under `config/`.
- Safety thresholds live in **one** file and are logged at startup with the run.
- Traversability cost weights are experimental artefacts: record the weight set
  alongside the mission-suite result it produced.

### Messages

Custom messages go in `drishti_msgs`. Prefer standard `sensor_msgs`,
`nav_msgs`, `vision_msgs` and `grid_map_msgs` types everywhere else — the
hardware transfer depends on the interface being conventional.

---

## Definition of done

A change is done when:

- [ ] It matches [SPEC.md](SPEC.md), or SPEC.md was updated in the same commit.
- [ ] It builds with `colcon build` and existing tests pass.
- [ ] New logic that can be tested without ROS running, is.
- [ ] No new node publishes to `/cmd_vel` or to a TF edge it does not own.
- [ ] New parameters are in `config/`, not in source.
- [ ] Any new dependency's licence is checked against REFERENCES.md §3.
- [ ] If it changes behaviour on the test suite, the run is recorded in
      [STATUS.md](STATUS.md) with before/after numbers.

---

## Working style

- **Verify against upstream, do not recall.** ROS 2, Nav2, RTAB-Map,
  `elevation_mapping_cupy` and Isaac Sim all move. Version-specific details in
  these documents are marked with an as-of date; re-check them before relying
  on them. This applies especially to the `Twist` vs `TwistStamped` question
  in SPEC.md §4.3 and to every licence claim.
- **Reproduce before fixing.** Most bugs here are frame, timestamp or
  calibration problems wearing an algorithm's costume. Check TF and clocks
  first.
- **Prefer configuration over code.** Nav2, RTAB-Map and the elevation mapper
  are highly tunable. Reach for a parameter before writing a node.
- **Small vocabularies.** Add a semantic class only when it changes a
  navigation decision.
- **Say what failed.** If a test fails or a step was skipped, report it with
  the output. Do not round results up.

---

## Things not to do

- Do not add a second SLAM system to the runtime graph.
- Do not train a custom model before the full loop runs with pretrained
  perception and failure analysis justifies it.
- Do not force motion when the planner reports no valid path.
- Do not let the supervisor's stop decision depend on a confidence score.
- Do not install every upstream repository at once — dependency conflicts are a
  real and expensive failure mode here (SETUP.md §3).
- Do not vendor GPLv3 code.
- Do not add LiDAR to the design. This is a vision-first problem statement.
