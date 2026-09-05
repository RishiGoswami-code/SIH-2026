# STATUS — DRISHTI-UGV

Living state of the project. **This is the handover document** — if someone
picks this up cold, this file plus [TASK.md](TASK.md) should tell them exactly
where things stand and what to do next.

Update it whenever a phase moves, a decision is made, or a suite is run.

---

## Snapshot

| | |
|---|---|
| **Phase** | Phase 0 — started, **partially blocked** |
| **Last updated** | 5 September 2026 |
| **Next action** | Decide the compute path — **B3**. Nothing else in Phase 0 can proceed. |
| **Hard deadline** | **30 September 2026** — SIH idea submission |
| **Blocked on** | Compute (B3, hard), Team ID (B1, submission only) |

> **The development machine cannot run the specified stack.** The GPU audit
> that closed Q2 came back negative on every axis — no NVIDIA GPU at all. This
> is the dominant fact about the project right now; see **B3** and
> **Decision log D11**. The workspace skeleton has been written and
> syntax-checked, but nothing has been built or run.

---

## Done

| # | Item | Date |
|---|---|---|
| 1 | Research baseline and architecture (blueprint, 29 sections + appendices) | 4 Sep 2026 |
| 2 | Problem statement verified against the SIH portal — **Category: Software, Theme: Smart Automation**, deadline 30 Sep 2026 | 4 Sep 2026 |
| 3 | Official SIH 2026 idea template downloaded | 4 Sep 2026 |
| 4 | Idea submission deck built — 6 slides, official template, PDF exported | 4 Sep 2026 |
| 5 | Project documentation set written (PRD, SPEC, SETUP, TASK, EVALUATION, REFERENCES, CLAUDE) | 4 Sep 2026 |
| 6 | Repository pushed to `github.com/RishiGoswami-code/SIH-2026` | 4 Sep 2026 |
| 7 | **Workstation hardware audited — fails the Isaac Sim floor on every axis** (Q2 closed, A2 falsified) | 5 Sep 2026 |
| 8 | `ugv_ws` colcon skeleton: `drishti_msgs` (`SafetyState`, `PerceptionHealth`) and `drishti_bringup` (shared params, `use_sim_time` global) — syntax-checked, **not built** | 5 Sep 2026 |
| 9 | **Safety supervisor decision core written and tested — 377 checks, 0 failures, clean under `-Wall -Wextra -Wpedantic -Werror`.** ROS-free by design, so it was verifiable on the blocked machine | 5 Sep 2026 |
| 10 | `tools/check_contract_sync.py` — guards `.msg` constants against the C++ enums and the header defaults against `drishti.yaml`; negative-tested | 5 Sep 2026 |
| 11 | **SPEC.md §9.1 ordering defect found and corrected** (D13), plus §4.2 topic and three §9.3 parameters added | 5 Sep 2026 |

## In progress

**Phase 0**, tasks 6–7 of 9 done (workspace skeleton, shared config). Tasks 1–5
and 8–9 need a machine that can run ROS 2 and a simulator, and are held behind
**B3**.

Ahead of schedule, out of phase order (D14): the **safety supervisor decision
core** is written and tested — 377 checks, clean under `-Werror`. Its ROS
wrapper and launch file are written but **have never been compiled or run**.

An NVIDIA laptop and an Apple-silicon laptop are reported available (5 Sep
2026). **Neither has been audited.** The NVIDIA machine's exact GPU decides
whether Isaac Sim is possible at all — a GTX part has no RT cores and fails the
same way the current machine does. Apple silicon cannot run Isaac Sim under any
configuration. Until the NVIDIA GPU model, VRAM and RAM are known, B3 stays
open.

## Next actions

1. **Decide the compute path — B3.** Cloud GPU, a team member's RTX machine, or
   a CPU-only downgrade. This is the only thing that matters right now; every
   remaining Phase 0 task depends on it, and the choice changes SPEC.md §2
   (see D11).
2. **Get the Team ID** from the SIH portal and fill it on the title slide (B1).
3. Once B3 is decided: install ROS 2 Jazzy, build `ugv_ws`, and record the
   exact toolchain versions in *Pinned versions* below.

---

## Blockers

| # | Blocker | Blocks | Owner | Since |
|---|---|---|---|---|
| B1 | Team ID not yet available from the portal | Title slide of the submission | Team | 4 Sep 2026 |
| ~~B2~~ | ~~Workstation GPU capability unconfirmed~~ — **closed 5 Sep 2026**, audit below. Superseded by B3. | — | — | — |
| **B3** | **No machine available that can run the specified stack** | **All of Phase 0 except the skeleton; every later phase** | **Team** | **5 Sep 2026** |

### B3 — the hardware audit

Measured on the development machine, 5 September 2026:

| Requirement (SETUP.md §1 / Isaac Sim 6.0.1 minimum) | Required | Actual | |
|---|---|---|---|
| GPU | NVIDIA RTX, RT cores required | **Intel Iris Xe (integrated)** | ✗ |
| VRAM | 16 GB | ~3.8 GB shared | ✗ |
| RAM | 32 GB | **7.7 GB** | ✗ |
| Free disk | 50 GB | 8.7 GB on C:, 56 GB on D: | ✗ on C: |
| CPU | 4+ cores | i5-1235U, 10c/12t | ✓ |
| OS | Ubuntu 24.04 | Windows 11, **WSL not installed** | ✗ |

Three consequences, in order of severity:

1. **Isaac Sim is impossible here, not merely slow.** It requires RT cores.
   Intel Iris Xe has none. This is a hard capability gap, not a performance
   one.
2. **`elevation_mapping_cupy` is equally impossible.** CuPy is CUDA; there is
   no NVIDIA GPU. The GPU-accelerated terrain layer — the component SPEC.md §6
   is built around — cannot run on this machine under any settings.
3. **RAM is the quiet constraint.** At 7.7 GB total, even the Gazebo fallback
   with Nav2, RTAB-Map and RViz2 is marginal, and WSL2 would take a share of
   it. Disk is fixable (install the distro to D:); RAM is not.

The Gazebo Harmonic fallback already named in SPEC.md §2 covers consequence 1.
It does **not** cover 2 — that needs a CPU traversability layer built on
`grid_map` instead, which is a real change to SPEC.md §6 and new work not
currently in TASK.md.

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
| D11 | 5 Sep 2026 | **Phase 0 split: the machine-independent half was built, the rest held.** `ugv_ws` skeleton, `drishti_msgs` and the shared params file were written and syntax-checked without a ROS install | The interface contract (SPEC.md §4, §9) is fixed and does not depend on which simulator or machine wins. Writing it now keeps Phase 0 moving while B3 is open, and it transfers unchanged to whatever compute path is chosen | Yes — cheap to revise |
| D12 | 5 Sep 2026 | **`elevation_mapping_cupy` is not viable on the current machine** and D4's "custom grid map fallback" is now the live path unless a CUDA GPU is obtained | CuPy requires CUDA; the audited machine has no NVIDIA GPU. This is a capability gap, not a tuning problem | Yes — reverts if an RTX machine or cloud GPU is secured |
| D13 | 5 Sep 2026 | **SPEC.md §9.1 evaluation order corrected: all STOP conditions now precede the SLOW branch.** `command_not_finite` hoisted above the forwarding paths; `t_pose_stale`, `t_plan_stale`, `t_cmd_stale` added to §9.3; `/perception/nearest_obstacle` added to §4.2 | The original "first match wins" order forwarded a command whenever confidence was low — even with no valid path — so low confidence masked a harder fault. Reordering can only turn SLOW into STOP, never the reverse, so it cannot weaken the envelope. The extra thresholds close the same hole for the pose, plan and command streams | **No** — safety ordering |
| D14 | 5 Sep 2026 | **Safety supervisor built during Phase 0, ahead of its Phase 5 slot** | A deliberate exception to the phase gates (D6), taken because the core is pure logic with no ROS or hardware dependency and was the one substantial component fully verifiable on a machine that cannot run the stack. The gate's purpose — stopping a model from masking a broken foundation — is not weakened: this component has no model in it. The ROS node it wraps remains uncompiled and unproven | Yes |

---

## Assumptions in force

These are working assumptions, not verified facts. Each one is a place where
being wrong costs rework — revisit them when the corresponding question closes.

| # | Assumption | Falsified by | Related |
|---|---|---|---|
| A1 | A stereo or RGB-D camera is acceptable; monocular-only is not mandated at evaluation | BEL guidance | Q4 |
| ~~A2~~ | ~~The workstation GPU meets the Isaac Sim floor~~ — **FALSIFIED 5 Sep 2026** by the hardware audit. No NVIDIA GPU present. See B3. | *(falsified)* | Q2, B3 |
| A3 | No physical UGV before the Grand Finale; Phase 7 is contingent | BEL / SPOC | Q3 |
| A4 | The semantic taxonomy in SPEC.md §5.2 is sufficient; no BEL-specific classes required | BEL guidance | Q5 |
| A5 | Licence positions in REFERENCES.md still hold | Re-checking upstream | — |

---

## Pinned versions

Fill during Phase 0 and update on every deliberate upgrade. Empty rows are the
honest state, not an oversight.

**Still entirely empty as of 5 Sep 2026** — nothing is installed, because of
B3. These rows get filled at the first successful `colcon build`, not before.

### Development machine, as audited 5 Sep 2026

| | |
|---|---|
| CPU | 12th Gen Intel Core i5-1235U — 10 cores / 12 threads |
| RAM | 7.7 GB |
| GPU | Intel Iris Xe (integrated), ~3.8 GB shared — **no NVIDIA GPU** |
| GPU driver | Intel 32.0.101.5542 |
| OS | Windows 11 Home Single Language, build 26200 |
| WSL | not installed; hypervisor present, so WSL2 is available |
| Disk free | 8.7 GB on C:, 56 GB on D: |

Recorded so the constraint is not re-litigated from memory. See **B3**.

### Toolchain

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
