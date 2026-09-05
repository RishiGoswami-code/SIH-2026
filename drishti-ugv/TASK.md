# TASK — DRISHTI-UGV

Phased backlog. **Phase N+1 does not start until Phase N ships its runnable
artefact.** This is the mechanism that stops a sophisticated model from hiding
a broken TF tree, odometry or navigation foundation.

Legend: `[ ]` todo · `[~]` in progress · `[x]` done · `[!]` blocked

Durations are estimates from the research baseline, assuming one workstation
and a small team working in parallel where tasks are independent.

---

## Phase 0 — Environment · 1–2 days

**Artefact:** a machine that builds and runs an empty ROS 2 workspace, with
the simulator verified, TF and clock health provable.

- [ ] Install Ubuntu 24.04 and a matching NVIDIA driver
- [x] Confirm GPU meets the Isaac Sim floor — **decided: Gazebo Harmonic** (SETUP.md §1.3, D15)
- [ ] Install ROS 2 Jazzy; verify `ros2 topic list` and a talker/listener pair
- [ ] Install Gazebo Harmonic and the `ros_gz` bridge packages for Jazzy
- [ ] Verify the bridge: a Gazebo sensor topic reaches ROS 2 via `ros_gz_bridge`
- [x] Create the `colcon` workspace skeleton and `drishti_msgs` package
- [x] Add `config/` with a shared params file and `use_sim_time` set globally
- [ ] Pin versions: record exact ROS 2, Gazebo, CUDA and driver versions in STATUS.md
- [ ] Stand up `docker/` only if native dependencies conflict

**Acceptance**
- `colcon build` succeeds on a clean clone.
- The simulator publishes at least one ROS 2 topic that `ros2 topic echo` receives.
- `ros2 run tf2_tools view_frames` produces a tree with no duplicate publishers.
- Every running node reports `use_sim_time: true`.

**Do not yet:** any AI, any perception model, any training.

---

## Phase 1 — Simulated navigation · 2–4 days

**Artefact:** a virtual UGV that drives to a goal in Gazebo using simulator
odometry and Nav2.

- [ ] Build or import a simple UGV (differential/skid-steer) with a stereo camera and IMU
- [ ] Publish robot description; verify the static TF chain from SPEC.md §3.1
- [ ] Verify `/camera/rgb/image_raw`, `/camera/depth/image_rect_raw`, `/camera/camera_info`, `/imu/data`, `/odom`
- [ ] Confirm every message carries a real sensor timestamp, not publish time
- [ ] Install and configure Nav2; author `config/nav2.yaml`
- [ ] Wire Nav2 to publish `/cmd_vel_nav` (**not** `/cmd_vel`) — SPEC.md §4.3
- [ ] Pin `Twist` vs `TwistStamped` for the installed Nav2 version and record the choice
- [ ] Teleoperate the UGV; then send a fixed goal and reach it
- [ ] Set up RViz2 and Foxglove views; start recording rosbag2

**Acceptance**
- The UGV reaches a commanded goal repeatedly on flat terrain.
- The TF tree is clean while driving; no transform gaps or duplicate publishers.
- rosbag2 recordings replay.

**Do not yet:** SLAM, semantics, terrain cost.

---

## Phase 2 — Visual SLAM · 3–6 days

**Artefact:** GPS-free pose and a map, with drift quantified against ground truth.

- [ ] Calibrate the simulated stereo pair; verify `camera_info` matches
- [ ] Install `rtabmap_ros`; configure for stereo + IMU
- [ ] Establish `map → odom` from RTAB-Map only; remove any ground-truth pose from the graph
- [ ] Verify loop closure on a revisited route
- [ ] Log ground-truth pose from the simulator alongside every bag
- [ ] Implement ATE/RPE computation in `drishti_eval`
- [ ] Feed RTAB-Map pose into Nav2 and re-run the Phase 1 goal test
- [ ] Record baseline drift on Easy and Medium worlds

**Acceptance**
- Nav2 reaches goals using RTAB-Map pose with no GNSS anywhere in the graph.
- ATE and RPE are reported automatically, not eyeballed.
- Baseline drift recorded in STATUS.md (target: < 2% of distance travelled).

**Do not yet:** semantic AI.

---

## Phase 3 — Terrain and traversability · 4–7 days

**Artefact:** a traversability costmap layer that Nav2 actually plans against.

- [ ] Produce `/camera/points` from depth; verify the cloud in the correct frame
- [ ] Install `elevation_mapping_cupy`; validate GPU/CUDA compatibility
- [ ] Publish `/elevation_map` with height, variance, slope, roughness, visibility
- [ ] Check for map "float" — pose/depth timestamp desynchronisation
- [ ] Implement `drishti_traversability` fusion producing `/traversability` (SPEC.md §6.1)
- [ ] Implement the Nav2 costmap layer consuming it
- [ ] Implement the unknown-terrain rule: unobserved/low-visibility cells are expensive
- [ ] Author an initial weight set; make weights params, not constants
- [ ] Build the Hard world (ditches, rocks, slopes, narrow corridors)
- [ ] Verify the planner routes around a ditch rather than across it

**Acceptance**
- The traversability layer is visible in RViz2 and demonstrably changes the plan (FR-01).
- A ditch scenario (T07) is avoided without any semantic model in the loop.
- Cost weights are in `config/`, and the current set is recorded with its result.

**Do not yet:** custom model training.

---

## Phase 4 — Perception · 5–10 days

**Artefact:** semantic hazard and terrain classification fused into the cost.

- [ ] Stand up `drishti_perception` with a pretrained lightweight YOLO detector
- [ ] Publish `/perception/detections` and `/perception/health`
- [ ] Add segmentation for the terrain tiers in SPEC.md §5.2 — keep the vocabulary small
- [ ] Publish `/perception/semantic_mask` with stable class ids
- [ ] Project semantics into the elevation map as semantic layers
- [ ] Wire the `semantic` and `uncertainty` terms into the cost function
- [ ] Measure perception latency against the ≤ 100 ms budget; apply TensorRT if needed
- [ ] Generate synthetic training data **only if** failure analysis demands it (Isaac Sim is available offline for small scenes — D15)
- [ ] Ablation: stereo depth vs Depth Anything V2 Small

**Acceptance**
- Hazards appear in the annotated stream and in the obstacle cost (FR-02).
- Mud/water scenarios (T08, T09) are handled better with semantics than without — measured, not asserted.
- Perception latency is inside budget on the target machine.

**Do not yet:** complex multi-model fusion.

---

## Phase 5 — Safety supervisor · 2–4 days

**Artefact:** a deterministic gate on `/cmd_vel` with measured stop latency.

> **Partly built early, during Phase 0 — see STATUS.md D14.** The decision core
> is pure logic with no ROS or hardware dependency, so it was the one
> substantial component fully verifiable on a machine that cannot run the
> stack. Everything still unchecked below needs a running system.

- [x] Define `drishti_msgs/SafetyState` with reason codes
- [x] Implement the C++ supervisor per SPEC.md §9, ticking on its own timer — *core done and tested; the ROS node wrapping it is **uncompiled***
- [ ] Enforce the invariant: supervisor is the sole `/cmd_vel` publisher — *coded, unproven; needs `ros2 topic info /cmd_vel` on a live graph*
- [x] Implement all seven stop/slow conditions with fixed evaluation order — *and corrected the order; SPEC.md §9.1 had a defect (D13)*
- [x] Move every threshold into one params file, logged at startup
- [x] Unit-test the decision logic **without ROS running** — *377 checks, clean under `-Werror`*
- [ ] Build the Failure world: frozen camera, stale depth, SLAM loss, invalid commands
- [ ] Measure stop latency from fault injection to blocked command

**Acceptance**
- T16–T19 (camera dropout, depth dropout, SLAM loss, no valid path) all end in a safe halt.
- Stop latency < 200 ms, reported from logs.
- Decision logic has unit tests that run in CI without a simulator.

**Do not yet:** hardware.

---

## Phase 6 — Randomised testing · 5–10 days

**Artefact:** hundreds of automated missions with an auto-generated metrics report.

- [ ] Implement the scenario runner in `drishti_eval` (headless, seeded, repeatable)
- [ ] Implement domain randomisation (SPEC.md §10.3)
- [ ] Implement all metrics in EVALUATION.md §2
- [ ] Automate the full scenario catalog T01–T20
- [ ] Run ≥ 100 randomised missions; then scale toward 1000
- [ ] Generate a per-run report and a suite summary
- [ ] Triage failures by category; feed fixes back into Phases 3–5
- [ ] Record the headline numbers in STATUS.md

**Acceptance**
- Collision-free completion ≥ 95% on the randomised suite.
- Goal completion ≥ 97%.
- The report regenerates from a single command, from bags plus ground truth.

**Do not yet:** a real UGV.

---

## Phase 7 — Optimisation and hardware transfer · contingent

**Artefact:** a profiled stack, and a bring-up plan executed only if a vehicle exists.

- [ ] Profile CPU, GPU, RAM and VRAM under full load
- [ ] Reduce latency: model size, TensorRT, resolution, sensor rates
- [ ] Re-run the suite after every optimisation to catch regressions
- [ ] Containerise the validated stack
- [ ] Write the sensor driver shim that reproduces the SPEC.md §4 contract
- [ ] Execute the bring-up sequence in SPEC.md §12.1 — **strictly in order**
- [ ] Mandatory external hardware e-stop from bring-up step 8 onward

**Acceptance**
- Post-optimisation suite results are no worse than pre-optimisation.
- On hardware: repeated collision-free low-speed runs before any speed increase.

---

## Cross-cutting, do continuously

- [ ] Keep STATUS.md current — it is the handover document
- [ ] Update SPEC.md in the same commit as any interface change
- [ ] Screen every new dependency's licence before integrating (REFERENCES.md §3)
- [ ] Keep one ROS distribution across the whole project
- [ ] Record every experiment: parameters in, numbers out

---

## Submission track — runs in parallel, hard deadline

- [x] Research baseline and architecture (blueprint)
- [x] SIH 2026 idea presentation, 6 slides, official template
- [ ] **Fill Team ID on the title slide** (blocked on portal registration)
- [ ] Add a prototype/repository link to the references slide once code exists
- [ ] Export final PDF and upload — **due 30 September 2026**
- [ ] Prepare the 5-minute demo script (EVALUATION.md §8)
