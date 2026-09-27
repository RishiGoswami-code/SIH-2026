# CLOUD_DEMO_SCRIPT — the real system, pre-recorded

A submission video shot against the actual ROS 2 / Gazebo stack — not the HTML
prototype. Pre-recorded, not live, for the same reason as before: repeatable
takes.

> **Update, 27 September 2026 — read this first.** Written when 8 days
> remained and the plan was AWS. There's no budget for that now — see
> [FREE_SETUP.md](FREE_SETUP.md) for the free, no-billing-risk bring-up
> (GitHub Codespaces/Actions instead of AWS) and its own, harder-triaged
> priority order given only **3 days** remain. Read FREE_SETUP.md's §4
> before this file's §1 below — it supersedes the ordering here, and it also
> corrects one wrong command in this file's Scene 4 (see the note there).

> **Original note, 22 September 2026.** Nothing in this repository has ever
> been built or executed against real ROS/Gazebo (STATUS.md). This script is
> only shootable *after* a bring-up actually succeeds, and that bring-up has
> known, named risk: `rclcpp` API fixes, the CuPy/CUDA pairing, and
> unverified `gz` topic names. §1 below is a priority order for burning down
> that risk, not a guarantee every scene is achievable in time.

---

## 1. What to attempt, in order, and why

Not every phase carries equal risk or equal payoff. This order front-loads the
scenes that are both **safe to show** (the safety story is the strongest part
of this project) and **least likely to blow the schedule**.

| Priority | Phase | Payoff | Risk | Verdict |
|---|---|---|---|---|
| **1 — core** | 0: bring-up | nothing else is possible without it | `rclcpp` API drift, unverified `gz` topic names (SETUP.md §5) | must do, budget 1–2 days |
| **1 — core** | 1: Nav2 driving | a UGV actually reaching a goal in Gazebo — the baseline "it moves" proof | low; Nav2 + Gazebo is the most-trodden path in this stack | must do |
| **1 — core** | 5: safety stop | the frozen-camera catch (D18→D19) is the single most distinctive result in the project | low; the supervisor core is already compiled and 388/388 tested, only the ROS wrapper is new | must do |
| **2 — stretch** | 3: traversability + the ditch | visually the most impressive scene — a negative obstacle refused on step height alone | medium; first real exercise of `elevation_mapping_cupy`, which STATUS.md names as the likely first CUDA/CuPy failure point | attempt after 1 is solid |
| **3 — stretch** | 2: visual SLAM | "no GPS in the graph" is a strong claim, but only if loop closure and a measured ATE are real | **highest** — SETUP.md §4 calls dependency conflicts a "real and expensive failure mode," and RTAB-Map has the most moving parts of anything here | attempt last, only if days remain |

**If priority-2 or 3 don't land in time, that is not a failed demo.** A UGV
driving to a goal in a real simulator, with a safety supervisor that catches a
fault nothing else would notice, running on ROS 2 you can show `ros2 node
list` for — is a legitimate, honest, real product demo. Cutting SLAM out of
the video and saying so is a better outcome than claiming it works when the
loop closure was never actually verified.

**Suggested day budget** (adjust once Day 1 tells you how much friction the
build actually has):

| Day | Do |
|---|---|
| 1 | AWS instance up, Docker build, first `colcon build`, fix compile errors |
| 2 | SETUP.md §5 checklist green: topics, TF tree, `/cmd_vel` single-publisher, `use_sim_time` |
| 3 | Phase 1: teleop, then a commanded Nav2 goal, repeatably |
| 4 | Phase 5: safety supervisor node + `fault_injector`, all four faults reproduced live |
| 5 | **Record priority-1 footage now**, before attempting anything riskier — a video in hand beats a better video that doesn't exist |
| 6 | Stretch: Phase 3 (ditch), record if it lands |
| 7 | Stretch: Phase 2 (SLAM), record if it lands; otherwise edit priority-1 footage |
| 8 | Buffer, submission |

---

## 2. Recording setup

- **Screen-capture RViz2 or Foxglove**, not a phone pointed at a monitor.
  Foxglove over the SSH-tunnelled websocket bridge (CLOUD_SETUP.md §3) if
  you're recording from a laptop against the cloud box; RViz2 directly if
  you're recording the cloud box's own desktop via VNC.
- **Capture a terminal pane alongside the 3D view** — this is what makes the
  video "show logs" rather than just an animation. `ros2 topic echo
  /safety/state` running live in a corner of the frame is more convincing than
  any caption.
- **Record a rosbag2 of every take.** If a shot needs a re-record, replay the
  bag instead of re-running the sim — guarantees the second take matches the
  first, and gives you a fallback if the live capture has a glitch.
- Seed every run (SPEC.md's scenario generation is seeded by design) so a
  re-take is the same run, not a different one that happens to look similar.

---

## 3. The script

Scenes 1–4 are the **priority-1, must-ship** content. Scenes 5–6 are stretch —
include them only if that footage actually exists; do not storyboard around
footage you don't have yet.

### Scene 1 — the problem (0:00–0:15)

**On screen:** title card / deck problem-statement slide.

**Say:**
> "BEL's problem statement: an outdoor UGV, point A to point B, camera-only —
> no GPS. This is the system running on our own build — not a mockup."

### Scene 2 — the rig is real (0:15–0:40)

**On screen:** terminal pane, cloud box.

```bash
ros2 node list
gz topic -l
ros2 topic info /cmd_vel --verbose
```

**Say:**
> "This is ROS 2 Jazzy and Gazebo Harmonic, running on a cloud GPU instance.
> One publisher on `/cmd_vel` — the safety supervisor — nothing else can move
> this vehicle. That's not a convention, it's enforced."

### Scene 3 — driving (0:40–1:30)

**On screen:** RViz2/Foxglove — the UGV, the global plan (`/plan`), the local
costmap. Split-screen or picture-in-picture with a terminal running `ros2
topic echo /odom` or the Nav2 goal-status.

**Say:**
> "Point A, point B, set through Nav2. What you're watching is the actual
> planner and controller — MPPI evaluating the local environment, not a
> pre-baked path."

**Action:** let it reach the goal. Don't cut early — a full, boring, correct
run is the point.

### Scene 4 — the safety stop

**Two versions — use whichever you actually got running; see
[FREE_SETUP.md](FREE_SETUP.md) §4 for why the first is the safer bet with 3
days left.**

**4a — the standalone stop (lower risk, needs only the supervisor compiling):**

```bash
ros2 launch drishti_bringup safety.launch.py
ros2 topic echo /safety/state
```

**Say:**
> "With nothing feeding it — no simulator, no perception yet — the supervisor
> holds zero velocity from the very first tick. That's not a bug, it's the
> design: loss of input is a stop condition, not 'probably fine'."

**Action:** show whatever `reason` it actually reports first — don't script a
specific one in advance; read it off the real output.

**4b — the frozen-camera fault (stretch — needs the injector's `raw_` prefix
bridge wiring, which isn't in `safety.launch.py` as shipped; confirm it's
actually wired before planning to shoot this):**

```bash
ros2 run drishti_eval fault_injector --ros-args -p scenario:=T16_camera_freeze
ros2 topic echo /safety/state
```

Note the corrected command — the scenario is a ROS **parameter**
(`-p scenario:=...`), not a `--fault` command-line flag; that flag doesn't
exist.

**Say:**
> "Now we break something on purpose. The camera keeps publishing — fresh
> timestamps, every frame — but the content underneath stops changing. A
> liveness check alone can't catch this; we found the gap building our fault
> harness and closed it."

**Action:** zoom the terminal on the `SafetyState` message as it flips to
`action: ACTION_STOP`, `reason: REASON_CAMERA_FROZEN`, and read the `detail`
field's text on screen — this is the literal audit record SPEC.md's message
definition exists to produce, not a subtitle someone wrote afterward.

**Say:**
> "Stops immediately, with its own reason code. Not a generic fault — the
> right sensor, named, every time."

### Scene 5 — stretch: the ditch (2:30–3:00, include only if Phase 3 ran)

**On screen:** the Hard world, `/traversability` grid layered in RViz2 next
to the RGB feed.

**Say:**
> "A ditch is a negative obstacle — nothing sticks up, so an ordinary
> occupancy grid drives in. Here the cost function reads step height directly
> off the elevation map, and the plan bends around it before the vehicle gets
> close."

### Scene 6 — stretch: no GPS (3:00–3:30, include only if Phase 2 ran with a
**measured** ATE, not a visual "looks about right")

**On screen:** RTAB-Map's `/map`, the pose graph, and the `drishti_eval`
report output.

**Say:**
> "This position estimate has no GPS in it anywhere in the graph — it comes
> from RTAB-Map on stereo and IMU alone. Drift against ground truth, measured
> over this run: [read the actual number `evaluate_trajectory` printed]."

Never fill that bracket with a number that wasn't printed by
`evaluate_trajectory` on an actual run. EVALUATION.md §7.2's rule applies to
the video exactly as it applies to STATUS.md: no seed and parameter set behind
a number means it's an anecdote, not a result.

### Scene 7 — close (final :15–:20)

**On screen:** team slide.

**Say (if Scenes 5–6 didn't make it):**
> "The navigation and safety stack you just watched is running end to end on
> our own build. Terrain reasoning and visual SLAM are next — the simulator
> work and the cloud pipeline are already in place to run them."

**Say (if everything ran):**
> "Every decision you watched — the plan, the stop, the terrain cost — is the
> actual shipping code, running end to end, with no human in the loop."

Pick the sentence that matches what was actually recorded. Do not deliver the
second one over footage that only supports the first.

---

## 4. If the build isn't ready by Day 5

Fall back to the HTML prototype demo ([prototype/DEMO_SCRIPT.md](../prototype/DEMO_SCRIPT.md))
for the decision-logic scenes (terrain reasoning, the frozen-camera stop), and
be explicit on camera that those two are running the parity-verified logic
standalone while the full ROS/Gazebo integration is in progress — which is
true, and a materially better claim than either overclaiming a shaky cloud
recording or missing the deadline outright. STATUS.md's own rule applies:
report what actually ran, not what was supposed to.
