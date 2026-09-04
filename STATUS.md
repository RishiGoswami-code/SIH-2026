# STATUS — DRISHTI-UGV

Living state of the project. **This is the handover document** — if someone
picks this up cold, this file plus [TASK.md](TASK.md) should tell them exactly
where things stand and what to do next.

Update it whenever a phase moves, a decision is made, or a suite is run.

---

## Snapshot

| | |
|---|---|
| **Phase** | Pre-Phase 0 — planning complete, no code written |
| **Last updated** | 4 September 2026 |
| **Next action** | Answer Q2 (GPU capability), then start Phase 0 |
| **Hard deadline** | **30 September 2026** — SIH idea submission |
| **Blocked on** | Team ID (submission), GPU confirmation (Phase 0) |

---

## Done

| # | Item | Date |
|---|---|---|
| 1 | Research baseline and architecture (blueprint, 29 sections + appendices) | 4 Sep 2026 |
| 2 | Problem statement verified against the SIH portal — **Category: Software, Theme: Smart Automation**, deadline 30 Sep 2026 | 4 Sep 2026 |
| 3 | Official SIH 2026 idea template downloaded | 4 Sep 2026 |
| 4 | Idea submission deck built — 6 slides, official template, PDF exported | 4 Sep 2026 |
| 5 | Project documentation set written (PRD, SPEC, SETUP, TASK, EVALUATION, REFERENCES, CLAUDE) | 4 Sep 2026 |

## In progress

Nothing. Phase 0 has not started.

## Next actions

1. **Confirm the workstation GPU** against the Isaac Sim floor (SETUP.md §1).
   This decides Isaac Sim vs Gazebo Harmonic and is the only hard blocker on
   Phase 0.
2. **Get the Team ID** from the SIH portal and fill it on the title slide.
3. Start Phase 0 — environment bring-up (TASK.md).

---

## Blockers

| # | Blocker | Blocks | Owner | Since |
|---|---|---|---|---|
| B1 | Team ID not yet available from the portal | Title slide of the submission | Team | 4 Sep 2026 |
| B2 | Workstation GPU capability unconfirmed | Phase 0 simulator decision | Team | 4 Sep 2026 |

---

## Decision log

Decisions with consequences. Append; do not rewrite history.

| # | Date | Decision | Rationale | Reversible? |
|---|---|---|---|---|
| D1 | 4 Sep 2026 | Hybrid stack over building from scratch | The research gap is integration under a vision-first outdoor constraint, not new SLAM or planning algorithms | Yes, but expensive |
| D2 | 4 Sep 2026 | RTAB-Map as the single runtime SLAM system | ROS 2 support with stereo/RGB-D and Nav2 integration examples; ORB-SLAM3 is GPLv3 and carries an older integration burden | Yes — ORB-SLAM3 remains an offline benchmark |
| D3 | 4 Sep 2026 | Nav2 + MPPI for planning and control | Mature framework; MPPI evaluates future trajectories against the local environment rather than following a geometric line | Yes — RPP/DWB fallback |
| D4 | 4 Sep 2026 | `elevation_mapping_cupy` for terrain | GPU-accelerated, ROS 2 Jazzy releases, semantic layers, MIT | Yes — custom grid map fallback |
| D5 | 4 Sep 2026 | Safety supervisor sits outside the AI and owns `/cmd_vel` | The stop decision must never depend on a model's confidence | **No** — this is a core invariant |
| D6 | 4 Sep 2026 | Simulation-first with phase gates | Prevents a sophisticated model from masking a broken TF, odometry or navigation foundation | No |
| D7 | 4 Sep 2026 | Stereo/RGB-D preferred over monocular | Metric depth greatly simplifies elevation mapping and collision reasoning; Depth Anything V2 Small held as fallback | Yes — pending answer to Q4 |
| D8 | 4 Sep 2026 | Targets stated as mission-level metrics, never "100% accuracy" | Defensible, measurable, and a stronger competition story | No |
| D9 | 4 Sep 2026 | Idea framed as a **software module** | Portal confirms PS 26126 is Category: Software; the earlier working assumption of Hardware was wrong | No |
| D10 | 4 Sep 2026 | Deck generated from `build_deck.py` rather than hand-edited | Reproducible, and re-exportable when team details change | Yes |

---

## Assumptions in force

These are working assumptions, not verified facts. Each one is a place where
being wrong costs rework — revisit them when the corresponding question closes.

| # | Assumption | Falsified by | Related |
|---|---|---|---|
| A1 | A stereo or RGB-D camera is acceptable; monocular-only is not mandated at evaluation | BEL guidance | Q4 |
| A2 | The workstation GPU meets the Isaac Sim floor | Checking the GPU | Q2, B2 |
| A3 | No physical UGV before the Grand Finale; Phase 7 is contingent | BEL / SPOC | Q3 |
| A4 | The semantic taxonomy in SPEC.md §5.2 is sufficient; no BEL-specific classes required | BEL guidance | Q5 |
| A5 | Licence positions in REFERENCES.md still hold | Re-checking upstream | — |

---

## Pinned versions

Fill during Phase 0 and update on every deliberate upgrade. Empty rows are the
honest state, not an oversight.

| Component | Version | Pinned on |
|---|---|---|
| Ubuntu | | |
| NVIDIA driver | | |
| ROS 2 | | |
| Isaac Sim | | |
| CUDA | | |
| Nav2 | | |
| RTAB-Map | | |
| `elevation_mapping_cupy` | | |
| Nav2 velocity message type (`Twist` / `TwistStamped`) | | |

---

## Results log

One row per mission-suite run. A row without a seed and a parameter set is an
anecdote, not a result (EVALUATION.md §7.2).

| Date | Commit | Suite | Runs | Collision-free | Goal completion | Drift | Notes |
|---|---|---|---|---|---|---|---|
| — | — | — | — | — | — | — | No runs yet |

---

## Submission tracker

| Item | State |
|---|---|
| Official template downloaded | Done |
| 6-slide deck on the official template | Done |
| PDF exported | Done |
| Team name on all slides | Done — The Vikings |
| SIH 2025 finalist credit | Done — title slide ribbon and per-slide badge |
| **Team ID on the title slide** | **Outstanding — B1** |
| Prototype / repository link on the references slide | Outstanding — needs code |
| Uploaded to the portal | Not yet — due **30 September 2026** |
| Demo script prepared | Not yet — EVALUATION.md §8 |
