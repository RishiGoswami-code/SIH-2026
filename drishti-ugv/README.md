# DRISHTI-UGV

Vision-first autonomous navigation for an outdoor Unmanned Ground Vehicle in
GPS-denied environments.

**Smart India Hackathon 2026 · Problem Statement 26126 · Bharat Electronics Limited**

| | |
|---|---|
| Problem Statement ID | 26126 (`SIH26126`) |
| Title | Vision Based Autonomous Navigation for Unmanned Ground Vehicle for Outdoor environment |
| Organisation | Bharat Electronics Limited (BEL) |
| Category | **Software** |
| Theme | Smart Automation |
| Idea submission deadline | **30 September 2026** |
| Team | The Vikings |

---

## What this is

A ROS 2 software module that drives a UGV from Point A to Point B across
unstructured outdoor terrain using cameras as the primary sensor, with **no
reliance on GPS**.

The system is deliberately a *hybrid*: mature open-source robotics carries the
infrastructure (SLAM, elevation mapping, navigation), and our engineering
concentrates on the three places where this problem is genuinely specific —

1. **the camera-to-traversability bridge** — turning vision geometry and
   semantics into a driving cost, not a binary occupancy grid;
2. **the safety supervisor** — a small deterministic module, outside the neural
   network, that owns the stop decision;
3. **the evaluation harness** — mission-level metrics scored automatically
   against simulator ground truth.

### Core principle

> The neural network only answers *"what am I looking at?"*.
> Coordinate transforms, mapping, planning, control and the stop decision stay
> in deterministic, auditable code — so a perception failure degrades into a
> safe halt, never a collision.

---

## Documents

Read them in this order.

| File | What it answers |
|---|---|
| [PRD.md](PRD.md) | What we are building and why; requirements and success criteria |
| [SPEC.md](SPEC.md) | How it is built: architecture, interfaces, algorithms, budgets |
| [SETUP.md](SETUP.md) | Machine requirements and the exact install order |
| [TASK.md](TASK.md) | The phased backlog — what to do next, with acceptance criteria |
| [EVALUATION.md](EVALUATION.md) | Metrics, the test scenario catalog, how we score ourselves |
| [REFERENCES.md](REFERENCES.md) | Upstream repositories, licences, official documentation |
| [STATUS.md](STATUS.md) | Living state of the project and the decision log |
| [CLAUDE.md](CLAUDE.md) | Working agreement for AI agents and contributors in this repo |

---

## Current state

**Pre-implementation.** No code has been written yet. The research baseline,
the architecture and the SIH idea submission deck are complete; Phase 0
(environment bring-up) is the next action. See [STATUS.md](STATUS.md).

---

## Stack

| Layer | Choice | Fallback |
|---|---|---|
| OS | Ubuntu 24.04 | — |
| Middleware | ROS 2 Jazzy | ROS 2 Humble |
| Simulator | NVIDIA Isaac Sim 6.x | Gazebo Harmonic |
| Localisation | RTAB-Map (stereo + IMU) | ORB-SLAM3 (offline benchmark only) |
| Terrain | `elevation_mapping_cupy` | custom grid map |
| Navigation | Nav2 + MPPI controller | Nav2 + RPP / DWB |
| Perception | YOLO detection + segmentation, stereo/RGB-D depth | Depth Anything V2 Small |
| Safety | custom deterministic supervisor | — |

Languages: **Python** (perception, tooling, evaluation) and **C++** (real-time
nodes, costmap layers, safety supervisor).

---

## Source material

These documents are derived from
`source/BEL_26126_Vision_Based_Autonomous_UGV_Technical_Blueprint.docx` (the
research and architecture baseline, information cutoff 4 September 2026) and
from the problem statement text published on `sih.gov.in`. The idea submission
deck and its generator are in `deck/`.

Software versions, compatibility and licence terms move. Anything quoted from
the blueprint is marked with its as-of date and **must be re-verified against
upstream before it is relied on**.
